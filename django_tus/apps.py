from pathlib import Path

from django.apps import AppConfig

from django_tus.conf import settings
from django_tus.errors import BAD_CONFIG_ERROR_TUS_DESTINATION_DIR
from django_tus.errors import BAD_CONFIG_ERROR_TUS_UPLOAD_DIR


def django_tus_config_check(app_configs, **kwargs):
    """
    Returns a list of errors in case the configured settings for
    `django-tus` are not valid. This function is used with the Django
    system check framework.
    """
    errors = []

    if not getattr(settings, 'TUS_UPLOAD_DIR', ''):
        errors.append(BAD_CONFIG_ERROR_TUS_UPLOAD_DIR)

    if not getattr(settings, 'TUS_DESTINATION_DIR', ''):
        errors.append(BAD_CONFIG_ERROR_TUS_DESTINATION_DIR)

    return errors


class DjangoTusConfig(AppConfig):

    name = 'django_tus'
    verbose_name = 'Django TUS'

    def ready(self):
        from django.core.checks import register, Tags
        register(django_tus_config_check, Tags.compatibility, deploy=False)
        Path(settings.TUS_DESTINATION_DIR).mkdir(parents=True, exist_ok=True)
        Path(settings.TUS_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

