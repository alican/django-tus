import os

import pytest

from django_tus.apps import django_tus_config_check
from django_tus.errors import BAD_CONFIG_ERROR_TUS_DESTINATION_DIR
from django_tus.errors import BAD_CONFIG_ERROR_TUS_UPLOAD_DIR


class TestDefaultSettings(object):

    def test_settings(self):
        errors = django_tus_config_check(['django_tus'])
        assert errors == []

        from django.conf import settings

        assert settings.TUS_UPLOAD_URL == '/media'
        assert settings.TUS_MAX_FILE_SIZE == 4294967296
        assert settings.TUS_FILE_OVERWRITE is True
        assert settings.TUS_TIMEOUT == 3600
        assert settings.TUS_UPLOAD_DIR == os.path.dirname(os.path.abspath(__file__)) + '/tmp/uploads'
        assert settings.TUS_DESTINATION_DIR == os.path.dirname(os.path.abspath(__file__)) + '/upload'


class TestManuallyConfiguredSettings(object):

    def test_configured_upload_dir(self, settings):
        settings.TUS_UPLOAD_DIR = '/tmp/django-tus/upload/dir'
        errors = django_tus_config_check(['django_tus'])
        assert errors == []

        from django.conf import settings
        assert settings.TUS_UPLOAD_DIR == '/tmp/django-tus/upload/dir'

    def test_configured_destination_dir(self, settings):
        settings.TUS_DESTINATION_DIR = '/tmp/django-tus/destination/dir'
        errors = django_tus_config_check(['django_tus'])
        assert errors == []

        from django.conf import settings
        assert settings.TUS_DESTINATION_DIR == '/tmp/django-tus/destination/dir'


class TestConfigErrors(object):

    @pytest.fixture()
    def settings_without_base_dir(self, settings):
        # According to https://github.com/pytest-dev/pytest-django/issues/33#issuecomment-18058652
        # this is the way how to fiddle with settings.
        del settings.BASE_DIR
        settings.TUS_UPLOAD_DIR = ''
        yield settings

    def test_unconfigured_upload_dir(self, settings_without_base_dir):
        errors = django_tus_config_check(['django_tus'])
        assert errors == [BAD_CONFIG_ERROR_TUS_UPLOAD_DIR]

    @pytest.fixture()
    def settings_without_media_root(self, settings):
        # According to https://github.com/pytest-dev/pytest-django/issues/33#issuecomment-18058652
        # this is the way how to fiddle with settings.
        del settings.MEDIA_ROOT
        settings.TUS_DESTINATION_DIR = ''
        yield settings

    def test_unconfigured_destination_dir(self, settings_without_media_root):
        errors = django_tus_config_check(['django_tus'])
        assert errors == [BAD_CONFIG_ERROR_TUS_DESTINATION_DIR]
