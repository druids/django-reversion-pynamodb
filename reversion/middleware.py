from django.conf import settings

from reversion.revisions import create_revision, set_user, set_comment, deactivate


class RevisionMiddleware:

    """Wraps the entire request in a revision."""

    manage_manually = False

    using = None

    def __init__(self, get_response):
        self.get_response = get_response
        self.atomic = getattr(settings, 'REVERSION_ATOMIC_REVISION', True)

    def __call__(self, request):
        with create_revision(manage_manually=self.manage_manually, using=self.using, atomic=self.atomic,
                             middleware=True):
            if hasattr(request, 'user') and request.user is not None and request.user.is_authenticated:
                set_user(request.user)
            set_comment('Request log from "RevisionMiddleware", path "{}"'.format(request.path))
            response = self.get_response(request)
        deactivate()
        return response

    def process_exception(self, request, exception):
        """Closes the revision."""
        deactivate()
