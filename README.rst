=============================
django-tus
=============================

.. image:: https://badge.fury.io/py/django-tus.png
    :target: https://badge.fury.io/py/django-tus

.. image:: https://travis-ci.org/alican/django-tus.png?branch=master
    :target: https://travis-ci.org/alican/django-tus

Django app implementing server side of tus protocol to powering resumable file uploads for django projects.

Supported Django/Python Versions
---------------------------------

    Django 2.2.x LTS and
    Django 3.0.x, 3.1.x, 3.2.x

    Python > 3.5

Documentation
-------------

The full documentation is at https://django-tus.readthedocs.org.

Example project
---------------

This example django project includes a javascript TUS demo client and implements django-tus as tus server:: https://github.com/alican/django-tus-example/

Quickstart
-------------

Install django-tus::

    pip install django-tus


Add 'django_tus' to your INSTALLED_APPS setting.::

    INSTALLED_APPS = (
    ...
    'django_tus',
    )

Add following urls to your urls.py.::

    path('upload/', TusUpload.as_view(), name='tus_upload'),
    path('upload/<uuid:resource_id>', TusUpload.as_view(), name='tus_upload_chunks'),


Configure and add this settings in your settings.py::

    TUS_UPLOAD_DIR = os.path.join(BASE_DIR, 'tus_upload')
    TUS_DESTINATION_DIR = os.path.join(BASE_DIR, 'media', 'uploads')
    TUS_FILE_NAME_FORMAT = 'increment'  # Other options are: 'random-suffix', 'random', 'keep'
    TUS_EXISTING_FILE = 'error'  #  Other options are: 'overwrite',  'error', 'rename'


Django has a setting for maximal memory size for uploaded files. This setting needs to be higher than the chunksize of
the tus client::

    DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

Todo
--------

* Concatenation Tus extension is not implemented
* More Tus-Extensions

Running Tests
--------------

Activate your virtual env, then install the testing requirements with `pip install -r requirements_test.txt`.

Run the tests with `pytest`.

You can even generate a coverage report with `pytest --cov=django_tus --cov-report=html`.

You can run `tox` to test against multiple Python and Django versions.

Credits
---------

    * http://tus.io/protocols/resumable-upload.html
    * https://github.com/matthoskins1980/Flask-Tus


MIT License
-------------

Copyright (c) 2020, Alican Toprak

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
