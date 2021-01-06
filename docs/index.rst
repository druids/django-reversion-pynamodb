.. _index:

django-reversion
================

**django-reversion** is an extension to the Django web framework that provides
version control for model instances.


Features
--------

-  Roll back to any point in a model instance's history.
-  Recover deleted model instances.
-  Simple admin integration.


Installation
------------

To install django-reversion:

1.  Install with pip: ``pip install django-reversion``.
2.  Add ``'reversion'`` and ``reversion.backends.sql`` to ``INSTALLED_APPS``.
3.  Run ``manage.py migrate``.


Admin integration
-----------------

django-reversion can be used to add rollback and recovery to your admin site.

.. include:: /_include/admin.rst

For more information about admin integration, see :ref:`admin`.


Low-level API
-------------

You can use the django-reversion API to build version-controlled applications. See :ref:`api`.


More information
----------------

Installation
^^^^^^^^^^^^

.. toctree::
   :maxdepth: 1

   common-problems
   changelog


Usage
^^^^^

.. toctree::
   :maxdepth: 2

   admin
   commands
   api
   views
   middleware
   errors
   signals
   backends
