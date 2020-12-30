from django.conf import settings
from django.http import HttpResponse
from django_tus import tus_api_version, tus_api_version_supported, tus_api_extensions


class TusResponse(HttpResponse):

    _base_tus_headers = {
        'Tus-Resumable': tus_api_version,
        'Tus-Version': ",".join(tus_api_version_supported),
        'Tus-Extension': ",".join(tus_api_extensions),
        'Tus-Max-Size': settings.TUS_MAX_FILE_SIZE,
        'Access-Control-Allow-Origin': "*",
        'Access-Control-Allow-Methods': "PATCH,HEAD,GET,POST,OPTIONS",
        'Access-Control-Expose-Headers': "Tus-Resumable,upload-length,upload-metadata,Location,Upload-Offset",
        'Access-Control-Allow-Headers': "Tus-Resumable,upload-length,upload-metadata,Location,Upload-Offset,content-type",
        'Cache-Control': 'no-store'
    }

    def add_headers(self, headers: dict):
        for key, value in headers.items():
            self.__setitem__(key, value)

    def __init__(self, extra_headers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_headers(self._base_tus_headers)
        if extra_headers:
            self.add_headers(extra_headers)
