from itertools import zip_longest

from pydjamodb.queryset import DynamoDBQuerySet


NULL_OBJ_KEY = '-'


class ObjectVersionDynamoDBQuerySet(DynamoDBQuerySet):

    def __init__(self, model):
        super().__init__(model)
        self._index = model.object_date_created_index
        self._prefetch_prev_versions = False
        self._scan_index_forward = False

    def _clone(self):
        c = super()._clone()
        c._prefetch_prev_versions = self._prefetch_prev_versions
        return c

    def set_index(self, index):
        raise RuntimeError('Value cannot be set')

    def prefetch_prev_versions(self):
        obj = self._clone()
        obj._prefetch_prev_versions = True
        return obj

    def _process_execution_with_prefetch_prev_version(self):
        """
        Execution prefetch prev version objects to loaded version.
        Because versions are ordered by creation date in queryset the result can be done with one or two DB requests.

        _scan_index_forward==True
        prev version of first object cannot be loaded from DB with this queryset
        and will not be preloaded (will be loaded with the lazy mannear of property prev_version in extra DB request)

         _scan_index_forward==True
         prev versions of all objects are loaded with one request. If limit is set it will be increased about 1 to
         get prev version for the last object and finally decreased back. If limit is not set the situation is much
         simplier because the last object has no prev version.
        """
        if self._scan_index_forward:
            super()._process_execution()

            reverse_results = self._results[::-1]
            self._prev_versions = reverse_results[1:]
            for version, prev_version in zip(reverse_results, self._prev_versions):
                version.prev_version = prev_version
        else:
            if self._limit:
                self._limit += 1
                super()._process_execution()
                self._limit -= 1

                results = self._results

                self._prev_versions = results[1:]
                # there are more results than limit
                self._results = results[:self._limit]
                for version, prev_version in zip_longest(self._results, self._prev_versions):
                    version.prev_version = prev_version
                if len(results) > self._limit:
                    self._next_key = {
                        key: self._results[-1].serialize()[key]
                        for key in self._execution.page_iter.key_names
                    }
            else:
                super()._process_execution()
                self._prev_versions = self._results[1:]
                for version, prev_version in zip_longest(self._results, self._prev_versions):
                    version.prev_version = prev_version

    def _process_execution(self):
        if self._prefetch_prev_versions:
            self._process_execution_with_prefetch_prev_version()
        else:
            super()._process_execution()

    def get_for_object_reference(self, model, object_id, model_db=None):
        from .models import get_key_from_content_type_and_id, _get_content_type

        return self.set_hash_key(
            get_key_from_content_type_and_id(_get_content_type(model), object_id, model_db)
        )

    def get_for_object(self, obj, model_db=None):
        return self.get_for_object_reference(obj.__class__, obj.pk, model_db=model_db)

    def get_for_model(self, model, model_db=None):
        from .models import get_object_content_type_key, _get_content_type

        return self._model.objects_all.set_index(self._model.object_content_type_created_index).set_hash_key(
            get_object_content_type_key(_get_content_type(model), model_db)
        )

    def get_deleted(self, model, model_db=None):
        from .models import get_object_content_type_key, _get_content_type

        return self._model.objects_all.set_index(self._model.object_content_type_key_removed_index).set_hash_key(
            get_object_content_type_key(_get_content_type(model), model_db)
        )


class RevisionDynamoDBQuerySet(DynamoDBQuerySet):

    def __init__(self, model):
        super().__init__(model)
        self._filter = self._get_filter(self._get_field('object_key'), 'eq',  NULL_OBJ_KEY)

    def all(self):
        return self.__class__(self._model)


class ObjectVersionRevisionDynamoDBQuerySet(DynamoDBQuerySet):

    def __init__(self, model):
        super().__init__(model)
        self._index = model.object_date_created_index
        self._prefetch_prev_versions = False
        self._hash_key = NULL_OBJ_KEY

    def all(self):
        return self.__class__(self._model)
