import base64
import logging
import os

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django_tus.conf import settings
from django_tus.response import TusResponse
from django_tus.signals import tus_upload_finished_signal
from django_tus.tusfile import TusFile, TusChunk, FilenameGenerator
from django.core.cache import cache
from pathvalidate import is_valid_filename, sanitize_filename


logger = logging.getLogger(__name__)

TUS_SETTINGS = {}


class TusUpload(View):
    on_finish = None

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):

        if not self.request.META.get("HTTP_TUS_RESUMABLE"):
            return TusResponse(status=405, content="Method Not Allowed")

        override_method = self.request.META.get('HTTP_X_HTTP_METHOD_OVERRIDE')
        if override_method:
            self.request.method = override_method

        return super(TusUpload, self).dispatch(*args, **kwargs)

    def finished(self):
        if self.on_finish is not None:
            self.on_finish()

    def get_metadata(self, request):
        metadata = {}
        if request.META.get("HTTP_UPLOAD_METADATA"):
            for kv in request.META.get("HTTP_UPLOAD_METADATA").split(","):
                splited_metadata = kv.split(" ")
                if len(splited_metadata) == 2:
                    key, value = splited_metadata
                    value = base64.b64decode(value)
                    if isinstance(value, bytes):
                        value = value.decode()
                    metadata[key] = value
                else:
                    metadata[splited_metadata[0]] = ""
        return metadata

    def options(self, request, *args, **kwargs):
        return TusResponse(status=204)

    def post(self, request, *args, **kwargs):

        metadata = self.get_metadata(request)

        metadata["filename"] = self.validate_filename(metadata)

        message_id = request.META.get("HTTP_MESSAGE_ID")
        if message_id:
            metadata["message_id"] = base64.b64decode(message_id)

        if settings.TUS_EXISTING_FILE == 'error' and settings.TUS_FILE_NAME_FORMAT == 'keep' and TusFile.check_existing_file(metadata.get("filename")):
            return TusResponse(status=409, reason="File with same name already exists")

        file_size = int(request.META.get("HTTP_UPLOAD_LENGTH", "0"))  # TODO: check min max upload size

        tus_file = TusFile.create_initial_file(metadata, file_size)

        return TusResponse(
            status=201,
            extra_headers={'Location': '{}{}'.format(request.build_absolute_uri(), tus_file.resource_id)})

    def head(self, request, resource_id):

        resource_id = str(resource_id)


        offset = cache.get("tus-uploads/{}/offset".format(resource_id))
        file_size = cache.get("tus-uploads/{}/file_size".format(resource_id))

        if offset is None:
            return TusResponse(status=404)

        return TusResponse(status=200,
                           extra_headers={
                               'Upload-Offset': offset,
                               'Upload-Length': file_size})

    def patch(self, request, resource_id, *args, **kwargs):

        tus_file = TusFile(str(resource_id))
        chunk = TusChunk(request)

        if not tus_file.is_valid():
            return TusResponse(status=410)

        if chunk.offset != tus_file.offset:
            return TusResponse(status=409)

        if chunk.offset > tus_file.file_size:
            return TusResponse(status=413)

        tus_file.write_chunk(chunk=chunk)

        if tus_file.is_complete():
            # file transfer complete, rename from resource id to actual filename
            tus_file.rename()
            tus_file.clean()

            self.send_signal(tus_file)
            self.finished()

        return TusResponse(status=204, extra_headers={'Upload-Offset': tus_file.offset})

    def send_signal(self, tus_file):
        tus_upload_finished_signal.send(
            sender=self.__class__,
            metadata=tus_file.metadata,
            filename=tus_file.filename,
            upload_file_path=tus_file.get_path(),
            file_size=tus_file.file_size,
            upload_url=settings.TUS_UPLOAD_URL,
            destination_folder=settings.TUS_DESTINATION_DIR)

    def validate_filename(self, metadata):
        filename = metadata.get("filename", "")
        if not is_valid_filename(filename):
            filename = FilenameGenerator.random_string(16)
        return filename


