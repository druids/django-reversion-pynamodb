from django.core import serializers
from django.core.serializers.base import DeserializationError
from django.db import models
from django.utils.encoding import force_str
from django.utils.translation import ugettext

from reversion.errors import RevertError
from reversion.revisions import _get_options


def get_object_version(model, data, object_repr, format):
    version_options = _get_options(model)
    data = force_str(data.encode('utf8'))
    try:
        return list(serializers.deserialize(format, data, ignorenonexistent=True,
                                            use_natural_foreign_keys=version_options.use_natural_foreign_keys))[0]
    except DeserializationError:
        raise RevertError(ugettext('Could not load %(object_repr)s version - incompatible version data.') % {
            'object_repr': object_repr,
        })
    except serializers.SerializerDoesNotExist:
        raise RevertError(ugettext('Could not load %(object_repr)s version - unknown serializer %(format)s.') % {
            'object_repr': object_repr,
            'format': format,
        })


def get_local_field_dict(model, object_version):
    """
    A dictionary mapping field names to field values in object version of the model.

    Parent links of inherited multi-table models will not be followed.
    """
    version_options = _get_options(model)
    obj = object_version.object
    field_dict = {}
    for field_name in version_options.fields:
        field = model._meta.get_field(field_name)
        if isinstance(field, models.ManyToManyField):
            # M2M fields with a custom through are not stored in m2m_data, but as a separate model.
            if object_version.m2m_data and field.attname in object_version.m2m_data:
                field_dict[field.attname] = object_version.m2m_data[field.attname]
        else:
            field_dict[field.attname] = getattr(obj, field.attname)
    return field_dict
