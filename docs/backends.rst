.. _backends:

Backends
========

You can use two reversion backends for storing version changes.

SQL
---

SQL backend stores data to the SQL database. It is the simpler solution but it is not optional for bigger projects with higher number of data changes. For these projects it is better to the use dynamodb backend.

To use SQL backend add ``reversion.backends.sql`` to the Django ``INSTALLED_APPS``.

DynamoDB
--------

DynamoDB backend stores versions in the AWS DynamoDB NoSQL database. This database is ideal for storing "big data".

To use DynamoDB backend add ``reversion.backends.dynamodb`` to the Django ``INSTALLED_APPS``, set ``PYDJAMODB_DATABASE`` configuration (https://github.com/druids/pydjamodb) and run command ``manage.py initdynamodbreversion`` to init DynamoDB indexes.
