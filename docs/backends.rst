.. _backends:

Backends
========

You can use several reversion backends for storing version changes. The default backend is SQL but reversion provides DynamoDB backend too.


Installation
------------

For DynamoDB backend you switch ``reversion.backends.sql`` for ``reversion.backends.dynamodb`` and run ``manage.py initdynamodbreversion``

Usage
-----

Usage is similar to ``SQL`` backend but you must import models from ``reversion.backends.dynamodb.models``. Be careful the NoSQL database is not the same as SQL. Some DB queries can be limited.