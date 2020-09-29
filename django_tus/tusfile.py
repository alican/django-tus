import logging
import os
import uuid
import string
import random
from django.core.files import File
from django.core.files.storage import FileSystemStorage

from django.conf import settings
from django.core.cache import cache

from django_tus.response import TusResponse

logger = logging.getLogger(__name__)


class FilenameGenerator:
    def __init__(self, filename: str = None):
        if not filename or not isinstance(filename, str):
            filename = self.random_string()
        self.filename = filename

    def get_name_and_extension(self):
        return os.path.splitext(self.filename)

    def create_random_name(self) -> str:
        name, extension = self.get_name_and_extension()
        random_string = FilenameGenerator.random_string()
        return "".join((random_string, extension))

    def create_random_suffix_name(self) -> str:
        name, extension = self.get_name_and_extension()
        random_string = FilenameGenerator.random_string()
        return "".join((name, ".", random_string, extension))

    @classmethod
    def random_string(cls, length: int = 11) -> str:
        letters_and_digits = string.ascii_letters + string.digits
        return''.join((random.choice(letters_and_digits) for i in range(length)))

    def create_incremented_name(self) -> str:
        index = 1
        name, extension = self.get_name_and_extension()
        while True:
            filename = '{}.{:04d}{}'.format(name, index, extension)
            index += 1
            if not os.path.lexists(os.path.join(settings.TUS_DESTINATION_DIR, filename)):
                break
        return filename


class TusFile:

    def get_storage(self):
        return FileSystemStorage()

    def __init__(self, resource_id):
        self.resource_id = resource_id
        self.filename = cache.get("tus-uploads/{}/filename".format(resource_id))
        self.file_size = int(cache.get("tus-uploads/{}/file_size".format(resource_id)))
        self.metadata = cache.get("tus-uploads/{}/metadata".format(resource_id))
        self.offset = cache.get("tus-uploads/{}/offset".format(resource_id))


    @staticmethod
    def create_initial_file(metadata, file_size):
        resource_id = str(uuid.uuid4())
        cache.add("tus-uploads/{}/filename".format(resource_id), "{}".format(metadata.get("filename")), settings.TUS_TIMEOUT)
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

        setting = settings.TUS_FILE_NAME_FORMAT

        if setting == 'keep':
            if self.check_existing_file(self.filename):
                return TusResponse(status=409, reason="File with same name already exists")
        elif setting == 'random':
            self.filename = FilenameGenerator(self.filename).create_random_name()
        elif setting == 'random-suffix':
            self.filename = FilenameGenerator(self.filename).create_random_suffix_name()
        elif setting == 'increment':
            self.filename = FilenameGenerator(self.filename).create_incremented_name()
        else:
            return ValueError()

        os.renames(self.get_path(), os.path.join(settings.TUS_DESTINATION_DIR, self.filename))


    def clean(self):
        cache.delete_many([
            "tus-uploads/{}/file_size".format(self.resource_id),
            "tus-uploads/{}/filename".format(self.resource_id),
            "tus-uploads/{}/offset".format(self.resource_id),
            "tus-uploads/{}/metadata".format(self.resource_id),
        ])

    def _write_file(self, path, offset, content):
        with open(path, "wb") as f:
            outfile = File(f)
            outfile.seek(offset)
            outfile.write(content)

    @staticmethod
    def check_existing_file(filename: str):
        return os.path.lexists(os.path.join(settings.TUS_DESTINATION_DIR, filename))


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
