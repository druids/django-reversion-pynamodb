from django.apps import AppConfig


class ReversionDynamoDBBackend(AppConfig):

    name = 'reversion.backends.dynamodb'
    label = 'reversion_backends_dynamodb'
