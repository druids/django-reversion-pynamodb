from django.db import migrations

from pydjamodb.connection import TableConnection


def clear_table(app, schema_editor):
    connection = TableConnection('reversion')
    if connection.exists_table():
        connection.delete_table(wait=True)


def create_reversion_table(apps, schema_editor):
    connection = TableConnection('reversion')
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


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.RunPython(clear_table),
        migrations.RunPython(create_reversion_table),
    ]
