from django.test.utils import override_settings
import reversion
from reversion.backends.sql.models import Version
from reversion.backends.dynamodb.models import Version as DynamoDBVersion
from test_app.models import (
    TestModel, TestModelRelated, TestModelParent, TestModelInline,
    TestModelNestedInline,
    TestModelInlineByNaturalKey, TestModelWithNaturalKey,
)
from test_app.tests.base import TestBase, TestModelMixin, TestModelParentMixin, TestModelParentWithoutFollowMixin
import json

from pydjamodb.tests import DynamoDBTestMixin


class GetForModelTest(DynamoDBTestMixin, TestModelMixin, TestBase):

    def testGetForModel(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_model(obj.__class__).count(), 1)

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testGetForModelDynamoDB(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_for_model(obj.__class__).count(), 1)


class GetForModelDbTest(TestModelMixin, TestBase):
    databases = {"default", "mysql", "postgres"}

    def testGetForModelDb(self):
        with reversion.create_revision(using="postgres"):
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.using("postgres").get_for_model(obj.__class__).count(), 1)

    def testGetForModelDbMySql(self):
        with reversion.create_revision(using="mysql"):
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.using("mysql").get_for_model(obj.__class__).count(), 1)


class GetForObjectTest(DynamoDBTestMixin, TestModelMixin, TestBase):

    def testGetForObject(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).count(), 1)

    def testGetForObjectEmpty(self):
        obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).count(), 0)

    def testGetForObjectOrdering(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        with reversion.create_revision():
            obj.name = "v2"
            obj.save()
        self.assertEqual(Version.objects.get_for_object(obj)[0].field_dict["name"], "v2")
        self.assertEqual(Version.objects.get_for_object(obj)[1].field_dict["name"], "v1")

    def testGetForObjectFiltering(self):
        with reversion.create_revision():
            obj_1 = TestModel.objects.create()
        with reversion.create_revision():
            obj_2 = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj_1).get().object, obj_1)
        self.assertEqual(Version.objects.get_for_object(obj_2).get().object, obj_2)

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testGetForObjectDynamoDB(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_for_object(obj).count(), 1)

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testGetForObjectEmptyDynamoDB(self):
        obj = TestModel.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_for_object(obj).count(), 0)


class GetForObjectDbTest(DynamoDBTestMixin, TestModelMixin, TestBase):
    databases = {"default", "mysql", "postgres"}

    def testGetForObjectDb(self):
        with reversion.create_revision(using="postgres"):
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).count(), 0)
        self.assertEqual(Version.objects.using("postgres").get_for_object(obj).count(), 1)

    def testGetForObjectDbMySql(self):
        with reversion.create_revision(using="mysql"):
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).count(), 0)
        self.assertEqual(Version.objects.using("mysql").get_for_object(obj).count(), 1)


class GetForObjectModelDbTest(DynamoDBTestMixin, TestModelMixin, TestBase):
    databases = {"default", "postgres"}

    def testGetForObjectModelDb(self):
        with reversion.create_revision():
            obj = TestModel.objects.db_manager("postgres").create()
        self.assertEqual(Version.objects.get_for_object(obj).count(), 0)
        self.assertEqual(Version.objects.get_for_object(obj, model_db="postgres").count(), 1)

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testGetForObjectModelDynamoDB(self):
        with reversion.create_revision():
            obj = TestModel.objects.db_manager("postgres").create()
        self.assertEqual(DynamoDBVersion.objects.get_for_object(obj).count(), 0)
        self.assertEqual(DynamoDBVersion.objects.get_for_object(obj, model_db="postgres").count(), 1)


class GetForObjectUniqueTest(TestModelMixin, TestBase):

    def testGetForObjectUnique(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        with reversion.create_revision():
            obj.save()
        self.assertEqual(len(list(Version.objects.get_for_object(obj).get_unique())), 1)

    def testGetForObjectUniqueMiss(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        with reversion.create_revision():
            obj.name = "v2"
            obj.save()
        self.assertEqual(len(list(Version.objects.get_for_object(obj).get_unique())), 2)


class GetForObjectReferenceTest(DynamoDBTestMixin, TestModelMixin, TestBase):

    def testGetForObjectReference(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk).count(), 1)

    def testGetForObjectReferenceEmpty(self):
        obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk).count(), 0)

    def testGetForObjectReferenceOrdering(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        with reversion.create_revision():
            obj.name = "v2"
            obj.save()
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk)[0].field_dict["name"], "v2")
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk)[1].field_dict["name"], "v1")

    def testGetForObjectReferenceFiltering(self):
        with reversion.create_revision():
            obj_1 = TestModel.objects.create()
        with reversion.create_revision():
            obj_2 = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj_1.pk).get().object, obj_1)
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj_2.pk).get().object, obj_2)

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testGetForObjectReferenceDynamoDB(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_for_object_reference(TestModel, obj.pk).count(), 1)

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testGetForObjectReferenceEmptyDynamoDB(self):
        obj = TestModel.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_for_object_reference(TestModel, obj.pk).count(), 0)


class GetForObjectReferenceDbTest(TestModelMixin, TestBase):
    databases = {"default", "postgres"}

    def testGetForObjectReferenceModelDb(self):
        with reversion.create_revision(using="postgres"):
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk).count(), 0)
        self.assertEqual(Version.objects.using("postgres").get_for_object_reference(TestModel, obj.pk).count(), 1)


class GetForObjectReferenceModelDbTest(TestModelMixin, TestBase):
    databases = {"default", "mysql", "postgres"}

    def testGetForObjectReferenceModelDb(self):
        with reversion.create_revision():
            obj = TestModel.objects.db_manager("postgres").create()
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk).count(), 0)
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk, model_db="postgres").count(), 1)

    def testGetForObjectReferenceModelDbMySql(self):
        with reversion.create_revision():
            obj = TestModel.objects.db_manager("mysql").create()
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk).count(), 0)
        self.assertEqual(Version.objects.get_for_object_reference(TestModel, obj.pk, model_db="mysql").count(), 1)


class GetDeletedTest(DynamoDBTestMixin, TestModelMixin, TestBase):
    databases = {"default", "mysql", "postgres"}

    def testGetDeleted(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        with reversion.create_revision():
            obj.save()
        obj.delete()
        self.assertEqual(Version.objects.get_deleted(TestModel).count(), 1)

    def testGetDeletedEmpty(self):
        with reversion.create_revision():
            TestModel.objects.create()
        self.assertEqual(Version.objects.get_deleted(TestModel).count(), 0)

    def testGetDeletedOrdering(self):
        with reversion.create_revision():
            obj_1 = TestModel.objects.create()
        with reversion.create_revision():
            obj_2 = TestModel.objects.create()
        pk_1 = obj_1.pk
        obj_1.delete()
        pk_2 = obj_2.pk
        obj_2.delete()
        self.assertEqual(Version.objects.get_deleted(TestModel)[0].object_id, str(pk_2))
        self.assertEqual(Version.objects.get_deleted(TestModel)[1].object_id, str(pk_1))

    def testGetDeletedPostgres(self):
        with reversion.create_revision(using="postgres"):
            obj = TestModel.objects.using("postgres").create()
        with reversion.create_revision(using="postgres"):
            obj.save()
        obj.delete()
        self.assertEqual(Version.objects.using("postgres").get_deleted(TestModel, model_db="postgres").count(), 1)

    def testGetDeletedMySQL(self):
        with reversion.create_revision(using="mysql"):
            obj = TestModel.objects.using("mysql").create()
        with reversion.create_revision(using="mysql"):
            obj.save()
        obj.delete()
        self.assertEqual(Version.objects.using("mysql").get_deleted(TestModel, model_db="mysql").count(), 1)

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testGetDeletedDynamoDB(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        with reversion.create_revision():
            obj.save()
        with reversion.create_revision():
            obj.delete()

        self.assertEqual(DynamoDBVersion.objects.get_deleted(TestModel).count(), 1)

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testGetDeletedEmptyDynamoDB(self):
        with reversion.create_revision():
            TestModel.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_deleted(TestModel).count(), 0)


class GetDeletedDbTest(TestModelMixin, TestBase):
    databases = {"default", "mysql", "postgres"}

    def testGetDeletedDb(self):
        with reversion.create_revision(using="postgres"):
            obj = TestModel.objects.create()
        obj.delete()
        self.assertEqual(Version.objects.get_deleted(TestModel).count(), 0)
        self.assertEqual(Version.objects.using("postgres").get_deleted(TestModel).count(), 1)

    def testGetDeletedDbMySql(self):
        with reversion.create_revision(using="mysql"):
            obj = TestModel.objects.create()
        obj.delete()
        self.assertEqual(Version.objects.get_deleted(TestModel).count(), 0)
        self.assertEqual(Version.objects.using("mysql").get_deleted(TestModel).count(), 1)


class GetDeletedModelDbTest(TestModelMixin, TestBase):
    databases = {"default", "postgres"}

    def testGetDeletedModelDb(self):
        with reversion.create_revision():
            obj = TestModel.objects.db_manager("postgres").create()
        obj.delete()
        self.assertEqual(Version.objects.get_deleted(TestModel).count(), 0)
        self.assertEqual(Version.objects.get_deleted(TestModel, model_db="postgres").count(), 1)


class FieldDictTest(DynamoDBTestMixin, TestModelMixin, TestBase):

    def testFieldDict(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).get().field_dict, {
            "id": obj.pk,
            "name": "v1",
            "related": [],
        })

    def testFieldDictM2M(self):
        obj_related = TestModelRelated.objects.create()
        with reversion.create_revision():
            obj = TestModel.objects.create()
            obj.related.add(obj_related)
        self.assertEqual(Version.objects.get_for_object(obj).get().field_dict, {
            "id": obj.pk,
            "name": "v1",
            "related": [obj_related.pk],
        })

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testFieldDictDynamoDB(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_for_object(obj).get().field_dict, {
            "id": obj.pk,
            "name": "v1",
            "related": [],
        })


class FieldDictFieldsTest(TestBase):

    def testFieldDictFieldFields(self):
        reversion.register(TestModel, fields=("name",))
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).get().field_dict, {
            "name": "v1",
        })


class FieldDictExcludeTest(TestBase):

    def testFieldDictFieldExclude(self):
        reversion.register(TestModel, exclude=("name",))
        with reversion.create_revision():
            obj = TestModel.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).get().field_dict, {
            "id": obj.pk,
            "related": [],
        })


class FieldDictInheritanceTest(DynamoDBTestMixin, TestModelParentMixin, TestBase):

    def testFieldDictInheritance(self):
        with reversion.create_revision():
            obj = TestModelParent.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).get().field_dict, {
            "id": obj.pk,
            "name": "v1",
            "related": [],
            "parent_name": "parent v1",
            "testmodel_ptr_id": obj.pk,
        })

    def testFieldDictInheritanceUpdate(self):
        obj = TestModelParent.objects.create()
        with reversion.create_revision():
            obj.name = "v2"
            obj.parent_name = "parent v2"
            obj.save()
        self.assertEqual(Version.objects.get_for_object(obj).get().field_dict, {
            "id": obj.pk,
            "name": "v2",
            "parent_name": "parent v2",
            "related": [],
            "testmodel_ptr_id": obj.pk,
        })

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testFieldDictInheritanceDynamoDB(self):
        with reversion.create_revision():
            obj = TestModelParent.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_for_object(obj).get().field_dict, {
            "id": obj.pk,
            "name": "v1",
            "related": [],
            "parent_name": "parent v1",
            "testmodel_ptr_id": obj.pk,
        })

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testFieldDictInheritanceUpdateDynamoDB(self):
        obj = TestModelParent.objects.create()
        with reversion.create_revision():
            obj.name = "v2"
            obj.parent_name = "parent v2"
            obj.save()
        self.assertEqual(DynamoDBVersion.objects.get_for_object(obj).get().field_dict, {
            "id": obj.pk,
            "name": "v2",
            "parent_name": "parent v2",
            "related": [],
            "testmodel_ptr_id": obj.pk,
        })


class FieldDictInheritanceWithoutFollowTest(DynamoDBTestMixin, TestModelParentWithoutFollowMixin, TestBase):

    def testFieldDictInheritanceWithoutParentFollow(self):
        with reversion.create_revision():
            obj = TestModelParent.objects.create()
        self.assertEqual(Version.objects.get_for_object(obj).get().field_dict, {
            "parent_name": "parent v1",
            "testmodel_ptr_id": obj.pk,
        })

    @override_settings(REVERSION_BACKEND='dynamodb')
    def testFieldDictInheritanceWithoutParentFollowDynamoDB(self):
        with reversion.create_revision():
            obj = TestModelParent.objects.create()
        self.assertEqual(DynamoDBVersion.objects.get_for_object(obj).get().field_dict, {
            "parent_name": "parent v1",
            "testmodel_ptr_id": obj.pk,
        })


class M2MTest(TestModelMixin, TestBase):

    def testM2MSave(self):
        v1 = TestModelRelated.objects.create(name="v1")
        v2 = TestModelRelated.objects.create(name="v2")
        with reversion.create_revision():
            obj = TestModel.objects.create()
            obj.related.add(v1)
            obj.related.add(v2)
        version = Version.objects.get_for_object(obj).first()
        self.assertEqual(set(version.field_dict["related"]), set((v1.pk, v2.pk,)))


class RevertTest(TestModelMixin, TestBase):

    def testRevert(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        with reversion.create_revision():
            obj.name = "v2"
            obj.save()
        Version.objects.get_for_object(obj)[1].revert()
        obj.refresh_from_db()
        self.assertEqual(obj.name, "v1")

    def testRevertBadSerializedData(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        Version.objects.get_for_object(obj).update(serialized_data="boom")
        with self.assertRaises(reversion.RevertError):
            Version.objects.get_for_object(obj).get().revert()

    def testRevertBadFormat(self):
        with reversion.create_revision():
            obj = TestModel.objects.create()
        Version.objects.get_for_object(obj).update(format="boom")
        with self.assertRaises(reversion.RevertError):
            Version.objects.get_for_object(obj).get().revert()


class RevisionRevertTest(TestModelMixin, TestBase):

    def testRevert(self):
        with reversion.create_revision():
            obj_1 = TestModel.objects.create(
                name="obj_1 v1"
            )
            obj_2 = TestModel.objects.create(
                name="obj_2 v1"
            )
        with reversion.create_revision():
            obj_1.name = "obj_1 v2"
            obj_1.save()
            obj_2.name = "obj_2 v2"
            obj_2.save()
        Version.objects.get_for_object(obj_1)[1].revision.revert()
        obj_1.refresh_from_db()
        self.assertEqual(obj_1.name, "obj_1 v1")
        obj_2.refresh_from_db()
        self.assertEqual(obj_2.name, "obj_2 v1")


class RevisionRevertDeleteTest(TestBase):

    def testRevertDelete(self):
        reversion.register(TestModel, follow=("related",))
        reversion.register(TestModelRelated)
        with reversion.create_revision():
            obj = TestModel.objects.create()
        obj_related = TestModelRelated.objects.create()
        with reversion.create_revision():
            obj.related.add(obj_related)
            obj.name = "v2"
            obj.save()
        Version.objects.get_for_object(obj)[1].revision.revert(delete=True)
        obj.refresh_from_db()
        self.assertEqual(obj.name, "v1")
        self.assertFalse(TestModelRelated.objects.filter(pk=obj_related.pk).exists())

    def testRevertDeleteNestedInline(self):
        reversion.register(TestModel, follow=("testmodelinline_set",))
        reversion.register(
            TestModelInline, follow=("testmodelnestedinline_set",))
        reversion.register(TestModelNestedInline)
        with reversion.create_revision():
            parent = TestModel.objects.create()
            child_a = TestModelInline.objects.create(
                test_model=parent)
            grandchild_a = TestModelNestedInline.objects.create(
                test_model_inline=child_a)

        with reversion.create_revision():
            child_b = TestModelInline.objects.create(
                test_model=parent)
            grandchild_b = TestModelNestedInline.objects.create(
                test_model_inline=child_b)
            reversion.add_to_revision(parent)

        Version.objects.get_for_object(parent)[1].revision.revert(delete=True)
        parent.refresh_from_db()
        self.assertRaises(
            TestModelInline.DoesNotExist,
            lambda: child_b.refresh_from_db()
        )

        self.assertRaises(
            TestModelNestedInline.DoesNotExist,
            lambda: grandchild_b.refresh_from_db()
        )
        self.assertEqual(
            list(parent.testmodelinline_set.all()), [child_a]
        )
        self.assertEqual(
            list(child_a.testmodelnestedinline_set.all()), [grandchild_a]
        )


class NaturalKeyTest(TestBase):

    def setUp(self):
        reversion.register(TestModelInlineByNaturalKey, use_natural_foreign_keys=True)
        reversion.register(TestModelWithNaturalKey)

    def testNaturalKeyInline(self):
        with reversion.create_revision():
            inline = TestModelWithNaturalKey.objects.create()
            obj = TestModelInlineByNaturalKey.objects.create(test_model=inline)
        self.assertEqual(json.loads(Version.objects.get_for_object(obj).get().serialized_data), [{
            'fields': {'test_model': ['v1']},
            'model': 'test_app.testmodelinlinebynaturalkey',
            'pk': 1
        }])
        self.assertEqual(Version.objects.get_for_object(obj).get().field_dict, {
            'test_model_id': 1,
            'id': 1,
        })
