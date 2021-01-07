=========================
django-reversion-pynamodb
=========================

|PyPI latest| |PyPI Version| |PyPI License| |TravisCI| |Docs|


**django-reversion-pynamodb** is an extension to the Django web framework that provides
version control for model instances. Library extends ``django-reversion-pynamodb`` library and provides
possibility to store version data in DynamoDB database.

Requirements
============

- Python 3.6 or later
- Django 2.2 or later

Features
========

-  Roll back to any point in a model instance's history.
-  Recover deleted model instances.
-  Simple admin integration.

Documentation
=============

Check out the latest ``django-reversion-pynamodb`` documentation at `Getting Started <http://django-reversion-pynamodb.readthedocs.io/>`_


Issue tracking and source code can be found at the
`main project website <http://github.com/druids/django-reversion-pynamodb>`_.

Upgrading
=========

Please check the `Changelog <https://github.com/druids/django-reversion-pynamodb/blob/master/CHANGELOG.rst>`_ before upgrading
your installation of django-reversion-pynamodb.

Contributing
============

Bug reports, bug fixes, and new features are always welcome. Please raise issues on the
`django-reversion-pynamodb project site <http://github.com/druids/django-reversion-pynamodb>`_, and submit
pull requests for any new code.

1. Fork the `repository <http://github.com/druids/django-reversion-pynamodb>`_ on GitHub.
2. Make a branch off of master and commit your changes to it.
3. Install requirements.

.. code:: bash

    $ pip install django psycopg2 mysqlclient -e .

4. Run the tests

.. code:: bash

    $ tests/manage.py test tests

5. Create a Pull Request with your contribution

Contributors
============

The django-reversion-pynamodb project was developed by `Dave Hall <http://www.etianen.com/>`_ and contributed
to by `many other people <https://github.com/druids/django-reversion-pynamodb/graphs/contributors>`_.


.. |Docs| image:: https://readthedocs.org/projects/django-reversion-pynamodb/badge/?version=latest
   :target: http://django-reversion-pynamodb.readthedocs.org/en/latest/?badge=latest
.. |PyPI Version| image:: https://img.shields.io/pypi/pyversions/django-reversion-pynamodb.svg?maxAge=60
   :target: https://pypi.python.org/pypi/django-reversion-pynamodb
.. |PyPI License| image:: https://img.shields.io/pypi/l/django-reversion-pynamodb.svg?maxAge=120
   :target: https://github.com/rhenter/django-reversion-pynamodb/blob/master/LICENSE
.. |PyPI latest| image:: https://img.shields.io/pypi/v/django-reversion-pynamodb.svg?maxAge=120
   :target: https://pypi.python.org/pypi/django-reversion-pynamodb
.. |TravisCI| image:: https://travis-ci.org/druids/django-reversion-pynamodb.svg?branch=master
   :target: https://travis-ci.org/druids/django-reversion-pynamodb
