#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = '0.5.0'

if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on github:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

history = open('HISTORY.rst').read().replace('.. :changelog:', '')

def read(f):
    return open(f, 'r', encoding='utf-8').read()

setup(
    name='django-tus',
    version=version,
    description="Django app implementing server side of tus v1.0.0 powering resumable file uploads for django projects",
    long_description=read('README.rst'),
    author='Alican Toprak',
    author_email='alican@querhin.com',
    url='https://github.com/alican/django-tus',
    packages=[
        'django_tus',
    ],
    include_package_data=True,
    install_requires=[
        'django>=2.2',
        'django-appconf',
        'pathvalidate==2.3.0'
    ],
    license="MIT",
    long_description_content_type='text/x-rst',
    zip_safe=False,
    keywords='django-tus',
    python_requires=">=3.5",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
