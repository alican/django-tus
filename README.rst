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



Todo
--------

* More Tus-Extensions

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements_test.txt
    (myenv) $ python runtests.py

Credits
---------



MIT License
---------

Copyright (c) 2016, Alican Toprak

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.





