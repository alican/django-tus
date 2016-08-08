=============================
django-tus
=============================

.. image:: https://badge.fury.io/py/django-tus.png
    :target: https://badge.fury.io/py/django-tus

.. image:: https://travis-ci.org/alican/django-tus.png?branch=master
    :target: https://travis-ci.org/alican/django-tus

Django app implementing server side of tus protocol to powering resumable file uploads for django projects.

Documentation
-------------

The full documentation is at https://django-tus.readthedocs.org.

Quickstart
----------

Install django-tus::

    pip install django-tus


Add 'django_tus' to your INSTALLED_APPS setting.::

    INSTALLED_APPS = (
    ...
    'django_tus',
)

Add following urls to your urls.px.::

    url(r'^upload/$', TusUpload.as_view(), name='tus_upload'),
    url(r'^upload/(?P<resource_id>[0-9a-z-]+)$', TusUpload.as_view(), name='tus_upload_chunks'),


Features
--------

* -

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ python runtests.py

Credits
---------

