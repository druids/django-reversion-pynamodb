import import_string

from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.base import SerializerDoesNotExist
from django.core import serializers


SERIALIZERS = (
    'reversion.serializers.json.JsonSerializer',
)


_serializers = {}


def get_serializer_formats():
    if not _serializers:
        _load_serializers()
    return list(_serializers)


def get_serializer(format):
    if not _serializers:
        _load_serializers()
    if format not in _serializers:
        raise SerializerDoesNotExist(format)
    return _serializers[format]


def serialize_instance(format, instance, **options):
    return get_serializer(format).serialize_instance(instance, **options)


def deserialize_instance(format, data, **options):
    return get_serializer(format).deserialize_instance(data, **options)


def deserialize_raw_fields(format, data, **options):
    return get_serializer(format).deserialize_raw_fields(data, **options)


def _load_serializers():
    for serializer_class_str in SERIALIZERS:
        try:
            serializer_class = import_string(serializer_class_str)
            _serializers[serializer_class.format] = serializer_class()
        except ImportError:
            raise ImproperlyConfigured(f'Missing reversion serializer with on path {serializer_class_str}')


class BaseSerializer:

    format = None

    def serialize_instance(self, instance, **options):
        return serializers.serialize(self.format, (instance,), **options)

    def deserialize_instance(self, data, **options):
        return list(serializers.deserialize(self.format, data, ignorenonexistent=True, **options))[0]

    def _deserialize_raw(self, data):
        raise NotImplementedError

    def deserialize_raw_fields(self, data):
        return self._deserialize_raw(data)[0]['fields']
