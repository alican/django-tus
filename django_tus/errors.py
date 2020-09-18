from django.core.checks import Error


BAD_CONFIG_ERROR_TUS_UPLOAD_DIR = Error(
    'Error while checking the configuration for "django-tus',
    hint='Is TUS_UPLOAD_DIR set correctly?',
    obj='django.conf.settings.TUS_UPLOAD_DIR',
    id='django-tus.E001',
)


BAD_CONFIG_ERROR_TUS_DESTINATION_DIR = Error(
    'Error while checking the configuration for "django-tus',
    hint='Is TUS_DESTINATION_DIR set correctly?',
    obj='django.conf.settings.TUS_DESTINATION_DIR',
    id='django-tus.E002',
)
