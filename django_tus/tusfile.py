import logging
import os
import random
import shutil
import string
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage

from django_tus.response import Tus404, TusResponse

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
        return "".join(random.choice(letters_and_digits) for i in range(length))

    def create_incremented_name(self) -> str:
        index = 1
        name, extension = self.get_name_and_extension()
        while True:
            filename = f"{name}.{index:04d}{extension}"
            index += 1
            if not os.path.lexists(os.path.join(settings.TUS_DESTINATION_DIR, filename)):
                break
        return filename


class TusFile:
    def get_storage(self):
        return FileSystemStorage()

    def __init__(self, resource_id: str):
        self.resource_id = resource_id
        self.filename = cache.get(f"tus-uploads/{resource_id}/filename")
        self.file_size = int(cache.get(f"tus-uploads/{resource_id}/file_size"))
        self.metadata = cache.get(f"tus-uploads/{resource_id}/metadata")
        self.offset = cache.get(f"tus-uploads/{resource_id}/offset")

    @staticmethod
    def get_tusfile_or_404(resource_id):
        if TusFile.resource_exists(str(resource_id)):
            return TusFile(resource_id)
        else:
            raise Tus404()

    @staticmethod
    def resource_exists(resource_id: str):
        return cache.get(f"tus-uploads/{resource_id}/filename", None) is not None

    @staticmethod
    def create_initial_file(metadata, file_size: int):
        resource_id = str(uuid.uuid4())
        cache.add(f"tus-uploads/{resource_id}/filename", "{}".format(metadata.get("filename")), settings.TUS_TIMEOUT)
        cache.add(f"tus-uploads/{resource_id}/file_size", file_size, settings.TUS_TIMEOUT)
        cache.add(f"tus-uploads/{resource_id}/offset", 0, settings.TUS_TIMEOUT)
        cache.add(f"tus-uploads/{resource_id}/metadata", metadata, settings.TUS_TIMEOUT)

        tus_file = TusFile(resource_id)
        tus_file.write_init_file()
        return tus_file

    def is_valid(self):
        return self.filename is not None and os.path.lexists(self.get_path())

    def get_path(self):
        return os.path.join(settings.TUS_UPLOAD_DIR, self.resource_id)

    def rename(self):
        setting = settings.TUS_FILE_NAME_FORMAT

        if setting == "keep":
            if self.check_existing_file(self.filename):
                return TusResponse(status=409, reason="File with same name already exists")
        elif setting == "random":
            self.filename = FilenameGenerator(self.filename).create_random_name()
        elif setting == "random-suffix":
            self.filename = FilenameGenerator(self.filename).create_random_suffix_name()
        elif setting == "increment":
            self.filename = FilenameGenerator(self.filename).create_incremented_name()
        else:
            return ValueError()

        shutil.move(self.get_path(), os.path.join(settings.TUS_DESTINATION_DIR, self.filename))

    def clean(self):
        cache.delete_many(
            [
                f"tus-uploads/{self.resource_id}/file_size",
                f"tus-uploads/{self.resource_id}/filename",
                f"tus-uploads/{self.resource_id}/offset",
                f"tus-uploads/{self.resource_id}/metadata",
            ],
        )

    @staticmethod
    def check_existing_file(filename: str):
        return os.path.lexists(os.path.join(settings.TUS_DESTINATION_DIR, filename))

    def write_init_file(self):
        try:
            with open(self.get_path(), "wb") as f:
                if self.file_size != 0:
                    f.seek(self.file_size - 1)
                    f.write(b"\0")
        except OSError as e:
            error_message = f"Unable to create file: {e}"
            logger.error(error_message, exc_info=True)
            return TusResponse(status=500, reason=error_message)

    def write_chunk(self, chunk):
        try:
            with open(self.get_path(), "r+b") as f:
                f.seek(chunk.offset)
                f.write(chunk.content)
            self.offset = cache.incr(f"tus-uploads/{self.resource_id}/offset", chunk.chunk_size)

        except OSError:
            logger.error(
                "patch",
                extra={
                    "request": chunk.META,
                    "tus": {
                        "resource_id": self.resource_id,
                        "filename": self.filename,
                        "file_size": self.file_size,
                        "metadata": self.metadata,
                        "offset": self.offset,
                        "upload_file_path": self.get_path(),
                    },
                },
            )
            return TusResponse(status=500)

    def is_complete(self):
        return self.offset == self.file_size

    def __str__(self):
        return f"{self.filename} ({self.resource_id})"


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
