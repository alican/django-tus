import base64
import logging
import os
import uuid

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django_tus.conf import settings
from django_tus.response import TusResponse
from django_tus.signals import tus_upload_finished_signal

logger = logging.getLogger(__name__)

TUS_SETTINGS = {}


class TusFile:
    def __init__(self, resource_id):
        self.resource_id = resource_id

        self.filename = cache.get("tus-uploads/{}/filename".format(resource_id))
        self.file_size = int(cache.get("tus-uploads/{}/file_size".format(resource_id)))
        self.metadata = cache.get("tus-uploads/{}/metadata".format(resource_id))
        self.offset = cache.get("tus-uploads/{}/offset".format(resource_id))


    @staticmethod
    def create_initial_file(metadata, file_size):
        logger.error(msg=metadata.get("filename"))
        resource_id = str(uuid.uuid4())

        cache.add("tus-uploads/{}/filename".format(resource_id), "{}".format(metadata.get("filename").decode('UTF-8')),
                  settings.TUS_TIMEOUT)
        cache.add("tus-uploads/{}/file_size".format(resource_id), file_size, settings.TUS_TIMEOUT)
        cache.add("tus-uploads/{}/offset".format(resource_id), 0, settings.TUS_TIMEOUT)
        cache.add("tus-uploads/{}/metadata".format(resource_id), metadata, settings.TUS_TIMEOUT)

        tus_file = TusFile(resource_id)
        tus_file.write_init_file()
        return tus_file

    def is_valid(self):
        return self.filename is not None and os.path.lexists(self.get_path())

    def get_path(self):
        return os.path.join(settings.TUS_UPLOAD_DIR, self.resource_id)

    def rename(self):

        self.filename = uuid.uuid4().hex + "_" + self.filename
        os.rename(self.get_path(), os.path.join(settings.TUS_DESTINATION_DIR, self.filename))

    def delete(self):
        cache.delete_many([
            "tus-uploads/{}/file_size".format(self.resource_id),
            "tus-uploads/{}/filename".format(self.resource_id),
            "tus-uploads/{}/offset".format(self.resource_id),
            "tus-uploads/{}/metadata".format(self.resource_id),
        ])

    def _write_file(self, path, offset, content):
        with open(path, "wb") as outfile:
            outfile.seek(offset)
            outfile.write(content)

    def write_init_file(self):
        try:
            self._write_file(self.get_path(), self.file_size, b"\0")
        except IOError as e:
            error_message = "Unable to create file: {}".format(e)
            logger.error(error_message, exc_info=True)
            return TusResponse(status=500, reason=error_message)

    def write_chunk(self, chunk):
        try:
            self._write_file(self.get_path(), chunk.offset, chunk.content)
            self.offset = cache.incr("tus-uploads/{}/offset".format(self.resource_id), chunk.chunk_size)

        except IOError:
            logger.error("patch", extra={'request': chunk.META, 'tus': {
                "resource_id": self.resource_id,
                "filename": self.filename,
                "file_size": self.file_size,
                "metadata": self.metadata,
                "offset": self.offset,
                "upload_file_path": self.get_path(),
            }})
            return TusResponse(status=500)

    def is_complete(self):
        return self.offset == self.file_size

    def __str__(self):
        return "{} ({})".format(self.filename, self.resource_id)


class TusInitFile:

    def __init__(self, offset, chunk_size, content):
        self.offset = offset
        self.chunk_size = chunk_size
        self.content = content


class TusChunk:
    def __init__(self, request):
        self.META = request.META
        self.offset = int(request.META.get("HTTP_UPLOAD_OFFSET", 0))
        self.chunk_size = int(request.META.get("CONTENT_LENGTH", 102400))
        self.content = request.body


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
                    metadata[key] = base64.b64decode(value)
                else:
                    metadata[splited_metadata[0]] = ""
        return metadata

    def options(self, request, *args, **kwargs):
        return TusResponse(status=204)

    def post(self, request, *args, **kwargs):

        metadata = self.get_metadata(request)

        message_id = request.META.get("HTTP_MESSAGE_ID")
        if message_id:
            metadata["message_id"] = base64.b64decode(message_id)

        self.check_existing_file(metadata.get("filename"))

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
            tus_file.delete()

            self.send_signal(tus_file)
            self.finished()

        return TusResponse(status=204, extra_headers={'Upload-Offset': tus_file.offset})

    @staticmethod
    def check_existing_file(filename: str):

        if settings.TUS_FILE_OVERWRITE:
            return

        if os.path.lexists(os.path.join(settings.TUS_UPLOAD_DIR, filename)):
            return TusResponse(status=409, reason="File already exists")

    def send_signal(self, tus_file):
        tus_upload_finished_signal.send(
            sender=self.__class__,
            metadata=tus_file.metadata,
            filename=tus_file.filename,
            upload_file_path=tus_file.get_path(),
            file_size=tus_file.file_size,
            upload_url=settings.TUS_UPLOAD_URL,
            destination_folder=settings.TUS_DESTINATION_DIR)


