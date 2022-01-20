import json

from reversion.serializers import BaseSerializer


class JsonSerializer(BaseSerializer):

    format = 'json'

    def _deserialize_raw(self, data):
        return json.loads(data)
