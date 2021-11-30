import import_string

from django.conf import settings


BACKENDS = [
    app_name.split('.')[-1] for app_name in settings.INSTALLED_APPS
    if isinstance(app_name, str) and app_name.startswith('reversion.backends.')
]

MODELS = {
    backend: import_string('reversion.backends.{}.models'.format(backend)) for backend in BACKENDS
}


def prepare_version_object(obj, content_type, object_id, model_db, version_options, explicit, using, is_delete):
    return MODELS[getattr(settings, 'REVERSION_BACKEND', None) or BACKENDS[0]].prepare_version_object(
        obj, content_type, object_id, model_db, version_options, explicit, using, is_delete
    )


def save_revision(date_created, user, comment, versions, using):
    return MODELS[getattr(settings, 'REVERSION_BACKEND', None) or BACKENDS[0]].save_revision(
        date_created, user, comment, versions, using
    )


def get_db_name():
    return MODELS[getattr(settings, 'REVERSION_BACKEND', None) or BACKENDS[0]].get_db_name()


def get_revision_or_none(id):
    return MODELS[getattr(settings, 'REVERSION_BACKEND', None) or BACKENDS[0]].get_revision_or_none(id)


if len(BACKENDS) == 1:
    Version = import_string('reversion.backends.{}.models.Version'.format(BACKENDS[0]))
    Reversion = import_string('reversion.backends.{}.models.Version'.format(BACKENDS[0]))
