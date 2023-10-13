#!/usr/bin/env python
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = "0.5.0"

if sys.argv[-1] == "publish":
    try:
        import wheel

        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    sys.exit()

if sys.argv[-1] == "tag":
    print("Tagging the version on github:")
    os.system(f"git tag -a {version} -m 'version {version}'")
    os.system("git push --tags")
    sys.exit()

history = open("HISTORY.md").read().replace(".. :changelog:", "")


def read(f):
    return open(f, encoding="utf-8").read()


setup(
    name="django-tus",
    version=version,
    description="Django app implementing server side of tus v1.0.0 powering resumable file uploads for Django projects",
    long_description=read("README.md"),
    author="Alican Toprak",
    author_email="alican@querhin.com",
    url="https://github.com/alican/django-tus",
    packages=[
        "django_tus",
    ],
    include_package_data=True,
    install_requires=[
        "django>=4.2",
        "django-appconf",
        "pathvalidate==3.0",
    ],
    license="MIT",
    long_description_content_type="text/x-rst",
    zip_safe=False,
    keywords="django-tus",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
    ],
)
