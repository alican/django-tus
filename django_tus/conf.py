import os

from appconf import AppConf
from django.conf import settings


class DjangoTusAppConf(AppConf):
    """
    The settings of `django-tus` powedered by the excellent `django-appconf` (not
    to confound with the Django app config).
    """

    class Meta:
        prefix = 'tus'

    UPLOAD_URL = '/media'
    MAX_FILE_SIZE = 4294967296  # in bytes, default is 4 GB
    FILE_OVERWRITE = True
    TIMEOUT = 3600  # in seconds
    UPLOAD_DIR = ''


    def configure_upload_dir(self, value):

        # The setting has been configured, return it.
        if value:
            return value

        # Build a default setting based on BASE_DIR, if available.
        if hasattr(settings, 'BASE_DIR'):
            return os.path.join(settings.BASE_DIR, 'tmp', 'uploads')

        # Setting is not configured.
        return ''

    DESTINATION_DIR = ''

    def configure_destination_dir(self, value):

        # The setting has been configured, return it.
        if value:
            return value

        # Build a default setting based on MEDIA_ROOT, if available.
        if hasattr(settings, 'MEDIA_ROOT'):
            return settings.MEDIA_ROOT

        # Setting is not configured.
        return ''

