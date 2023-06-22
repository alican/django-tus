import django.dispatch

tus_upload_finished_signal = django.dispatch.Signal()
"""
This signal provides the following keyword arguments:
    sender
    metadata
    resource_id
    filename
    upload_file_path
    file_size
    upload_url
    destination_folder
    request
"""
