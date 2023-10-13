import os

from django.conf import settings

from appconf import AppConf


class DjangoTusAppConf(AppConf):
    """
    The settings of `django-tus` powedered by the excellent `django-appconf` (not
    to confound with the Django app config).
    """

    class Meta:
        prefix = "tus"

    UPLOAD_URL = "/media"
    MAX_FILE_SIZE = 4294967296  # in bytes, default is 4 GB
    TIMEOUT = 3600  # in seconds
    UPLOAD_DIR = ""
    FILE_NAME_FORMAT = "increment"
    EXISTING_FILE = "error"
    DESTINATION_DIR = ""

    def configure_upload_dir(self, value):
        # The setting has been configured, return it.
        if value:
            return value

        # Build a default setting based on BASE_DIR, if available.
        if hasattr(settings, "BASE_DIR"):
            return os.path.join(settings.BASE_DIR, "tmp", "uploads")

        # Setting is not configured.
        return ""

    def configure_destination_dir(self, value):
        # The setting has been configured, return it.
        if value:
            return value

        # Build a default setting based on MEDIA_ROOT, if available.
        if hasattr(settings, "MEDIA_ROOT"):
            return os.path.join(settings.MEDIA_ROOT, "uploads")

        # Setting is not configured.
        return ""
