import django.dispatch


tus_upload_finished_signal = django.dispatch.Signal(
    providing_args=[
        "metadata",
        "filename",
        "upload_file_path",
        "file_size",
        "upload_url",
        "destination_folder"
    ]
)
