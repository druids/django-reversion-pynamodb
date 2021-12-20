from django.core.management.base import BaseCommand, CommandError

from pydjamodb.connection import TableConnection


class Command(BaseCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--noinput', '--no-input', action='store_false', dest='interactive',
            help='Tells Django to NOT prompt the user for input of any kind.',
        )

    def handle(self, **options):
        if options['interactive']:
            message = (
                'This will delete existing revisions!\n'
                'Are you sure you want to do this?\n\n'
                "Type 'yes' to continue, or 'no' to cancel: "
            )
            if input(message) != 'yes':
                raise CommandError('Init DynamoDB revisions cancelled.')

        self.stdout.write(f'Init DynamoDB revisions')

        connection = TableConnection('reversion')
        if connection.exists_table():
            connection.delete_table(wait=True)
        connection.create_table(
            **{
                'attribute_definitions': [
                    {'attribute_name': 'object_key', 'attribute_type': 'S'},
                    {'attribute_name': 'revision_id', 'attribute_type': 'S'},
                    {'attribute_name': 'date_created', 'attribute_type': 'S'},
                    {'attribute_name': 'object_content_type_key', 'attribute_type': 'S'},
                    {'attribute_name': 'is_removed', 'attribute_type': 'S'}
                ],
                'key_schema': [
                    {'key_type': 'RANGE', 'attribute_name': 'object_key'},
                    {'key_type': 'HASH', 'attribute_name': 'revision_id'}
                ],
                'global_secondary_indexes': [
                    {
                        'index_name': 'object_content_type_created_index',
                        'key_schema': [
                            {'AttributeName': 'date_created', 'KeyType': 'RANGE'},
                            {'AttributeName': 'object_content_type_key', 'KeyType': 'HASH'}
                        ],
                        'projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'index_name': 'object_content_type_key_removed_index',
                        'key_schema': [
                            {'AttributeName': 'is_removed', 'KeyType': 'RANGE'},
                            {'AttributeName': 'object_content_type_key', 'KeyType': 'HASH'}
                        ],
                        'projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'index_name': 'object_date_created_index',
                        'key_schema': [
                            {'AttributeName': 'date_created', 'KeyType': 'RANGE'},
                            {'AttributeName': 'object_key', 'KeyType': 'HASH'}
                        ],
                        'projection': {'ProjectionType': 'ALL'}
                    }
                ],
                'local_secondary_indexes': []
            },
            wait=True
        )