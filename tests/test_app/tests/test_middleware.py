from django.conf import settings
from django.test.utils import override_settings
from test_app.models import TestModel
from test_app.tests.base import TestBase, TestModelMixin, LoginMixin


use_middleware = override_settings(
    MIDDLEWARE=settings.MIDDLEWARE + ["reversion.middleware.RevisionMiddleware"],
)


@use_middleware
class RevisionMiddlewareTest(TestModelMixin, TestBase):

    def testCreateRevision(self):
        response = self.client.post("/test-app/save-obj/")
        obj = TestModel.objects.get(pk=response.content)
        self.assertSingleRevision((obj,), comment='Request log from "RevisionMiddleware", path "/test-app/save-obj/"')

    def testCreateRevisionError(self):
        with self.assertRaises(Exception):
            self.client.post("/test-app/save-obj-error/")
        self.assertNoRevision()


@use_middleware
class RevisionMiddlewareUserTest(TestModelMixin, LoginMixin, TestBase):

    def testCreateRevisionUser(self):
        response = self.client.post("/test-app/save-obj/")
        obj = TestModel.objects.get(pk=response.content)
        self.assertSingleRevision(
            (obj,), user=self.user, comment='Request log from "RevisionMiddleware", path "/test-app/save-obj/"'
        )

    @override_settings(REVERSION_ENABLED=False)
    def testDisabledRevision(self):
        response = self.client.post("/test-app/save-obj/")
        TestModel.objects.get(pk=response.content)
        self.assertNoRevision()