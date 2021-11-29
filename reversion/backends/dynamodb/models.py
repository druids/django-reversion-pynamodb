from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex

from pydjamodb.models import DynamoModel
from pydjamodb.attributes import BooleanUnicodeAttribute
from pydjamodb.queryset import DynamoDBManager

from uuid import uuid4

from django.core import serializers
from django.contrib.contenttypes.models import ContentType
from django.db import router
from django.utils.encoding import force_str
from django.utils.functional import cached_property

from reversion.backends.utils import get_object_version, get_local_field_dict
from reversion.revisions import _get_options
from reversion.signals import pre_revision_commit, post_revision_commit

from .queryset import (
    ObjectVersionDynamoDBQuerySet, RevisionDynamoDBQuerySet, ObjectVersionRevisionDynamoDBQuerySet, NULL_OBJ_KEY
)


def _get_content_type(model, using=None):
    version_options = _get_options(model)
    return ContentType.objects.db_manager(using).get_for_model(
        model,
        for_concrete_model=version_options.for_concrete_model,
    )


def get_key_from_content_type_and_id(content_type, object_id, model_db=None):
    model_db = model_db or router.db_for_write(content_type.model_class())
    return '|'.join((model_db, str(content_type.pk), str(object_id)))


def get_key_from_object(obj, model_db=None):
    if not obj:
        return NULL_OBJ_KEY
    else:
        return get_key_from_content_type_and_id(_get_content_type(obj), obj.pk, model_db)


def get_object_from_key_or_none(object_key):
    if not object_key or object_key == '-':
        return None

    model_db, content_type_id, object_id = object_key.split('|')

    return ContentType.objects.get(
        pk=content_type_id
    ).model_class().objects.using(model_db).filter(pk=object_id).first()


def get_object_content_type_key(content_type, model_db=None):
    model_db = model_db or router.db_for_write(content_type.model_class())
    return '{}|{}'.format(model_db, content_type.pk)


class VersionObjectDateCreatedIndex(GlobalSecondaryIndex):

    object_key = UnicodeAttribute(hash_key=True)
    date_created = UTCDateTimeAttribute(range_key=True)

    class Meta:
        projection = AllProjection()


class VersionModelDateCreatedIndex(GlobalSecondaryIndex):

    object_content_type_key = UnicodeAttribute(hash_key=True)
    date_created = UTCDateTimeAttribute(range_key=True)

    class Meta:
        projection = AllProjection()


class RemovedVersionIndex(GlobalSecondaryIndex):

    object_content_type_key = UnicodeAttribute(hash_key=True)
    is_removed = BooleanUnicodeAttribute(range_key=True)

    class Meta:
        projection = AllProjection()


class ReversionDynamoModel(DynamoModel):

    revision_id = UnicodeAttribute(hash_key=True)
    date_created = UTCDateTimeAttribute()
    user_key = UnicodeAttribute(null=True)
    comment = UnicodeAttribute(null=True)

    object_key = UnicodeAttribute(range_key=True, null=True)
    object_content_type_key = UnicodeAttribute(null=True)
    format = UnicodeAttribute(null=True)
    serialized_data = UnicodeAttribute(null=True)
    object_repr = UnicodeAttribute(null=True)
    is_removed = BooleanUnicodeAttribute(null=True)

    object_date_created_index = VersionObjectDateCreatedIndex()
    object_content_type_key_removed_index = RemovedVersionIndex()
    object_content_type_created_index = VersionModelDateCreatedIndex()

    class Meta:
        table_name = 'reversion'

    @cached_property
    def user(self):
        return get_object_from_key_or_none(self.user_key)


class Revision(ReversionDynamoModel):

    object_date_created_index = VersionObjectDateCreatedIndex()

    objects = RevisionDynamoDBQuerySet.as_manager()
    objects_version = ObjectVersionRevisionDynamoDBQuerySet.as_manager()

    class Meta:
        proxy = True

    @property
    def version_set(self):
        return Version.objects_all.set_hash_key(self.revision_id).filter(object_key__startswith='VERSION')


class Version(ReversionDynamoModel):

    object_date_created_index = VersionObjectDateCreatedIndex()
    object_content_type_key_removed_index = RemovedVersionIndex()
    object_content_type_created_index = VersionModelDateCreatedIndex()

    objects = ObjectVersionDynamoDBQuerySet.as_manager()
    objects_all = DynamoDBManager()

    class Meta:
        proxy = True

    @cached_property
    def revision(self):
        return Revision.get(self.revision_id, NULL_OBJ_KEY)

    @cached_property
    def _object_version(self):
        return get_object_version(self._model, self.serialized_data, self.object_repr, self.format)

    @cached_property
    def _local_field_dict(self):
        return get_local_field_dict(self._model, self._object_version)

    @cached_property
    def field_dict(self):
        """
        A dictionary mapping field names to field values in this version
        of the model.

        This method will follow parent links, if present.
        """
        field_dict = self._local_field_dict
        # Add parent data.
        for parent_model, field in self._model._meta.concrete_model._meta.parents.items():
            content_type = _get_content_type(parent_model)
            parent_id = field_dict[field.attname]
            try:
                parent_version = Version.get(
                    self.revision_id,
                    get_key_from_content_type_and_id(content_type, parent_id)
                )
                field_dict.update(parent_version.field_dict)
            except Version.DoesNotExist:
                pass
        return field_dict

    @cached_property
    def object(self):
        return get_object_from_key_or_none(self.object_key)

    @property
    def object_id(self):
        return self.object_key.split('|')[2]

    @property
    def content_type_id(self):
        return int(self.object_key.split('|')[1])

    @property
    def _content_type(self):
        return ContentType.objects.get_for_id(self.content_type_id)

    @property
    def _model(self):
        return self._content_type.model_class()

    @cached_property
    def prev_version(self):
        return Version.objects.set_hash_key(self.object_key).filter(
            date_created__lt=self.date_created
        ).first()

    @property
    def is_revision(self):
        return not self.object_content_type_key

    @property
    def is_version(self):
        return not self.is_revision

    @property
    def db(self):
        return self.object_content_type_key.split('|')[0]

    @property
    def is_delete(self):
        return bool(self.is_removed)

    def revert(self):
        self._object_version.save(using=self.db)


def prepare_version_object(obj, content_type, object_id, model_db, version_options, explicit, using, is_delete):
    object_key = get_key_from_content_type_and_id(content_type, object_id, model_db)
    version = Version(
        object_key=object_key,
        format=version_options.format,
        serialized_data=serializers.serialize(
            version_options.format,
            (obj,),
            fields=version_options.fields,
            use_natural_foreign_keys=version_options.use_natural_foreign_keys,
        ),
        object_repr=force_str(obj),
        is_removed=True if is_delete else None,
        object_content_type_key=get_object_content_type_key(content_type, model_db)
    )

    if version_options.ignore_duplicates and explicit:
        previous_version = Version.objects.set_index(
            Version.object_date_created_index
        ).filter(object=object_key).first()
        if not is_delete and previous_version and previous_version._local_field_dict == version._local_field_dict:
            return None

    return version


def save_revision(date_created, user, comment, versions, using):
    from reversion.revisions import create_revision

    # Generate random revision PK
    revision_id = str(uuid4())

    user_key = get_key_from_object(user)

    revision = ReversionDynamoModel(
        revision_id=revision_id,
        object_key=NULL_OBJ_KEY,
        date_created=date_created,
        user_key=user_key,
        comment=comment
    )

    # Send the pre_revision_commit signal.
    pre_revision_commit.send(
        sender=create_revision,
        revision=revision,
        versions=versions
    )

    # Save version models.
    with Version.batch_write() as batch:
        batch.save(revision)

        for version in versions:
            version.revision_id = revision_id
            version.date_created = date_created
            version.user_key = user_key
            version.comment = comment
            batch.save(version)
    post_revision_commit.send(
        sender=create_revision,
        revision=revision,
        versions=versions,
        revision_id=revision_id
    )
    return revision_id


def get_db_name():
    return None


def get_revision_or_none(id):
    try:
        return Revision.get(id, NULL_OBJ_KEY)
    except Version.DoesNotExist:
        return None
