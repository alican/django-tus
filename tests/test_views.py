from django.test import LiveServerTestCase
from django.urls import reverse

from tusclient import client


class TestUploadView(LiveServerTestCase):

    def test_get_is_not_allowed(self):
        response = self.client.get(reverse('tus_upload'))
        assert response.status_code == 405

    def test_upload_file(self):
        tus_client = client.TusClient(
            self.live_server_url + reverse('tus_upload')
        )
        uploader = tus_client.uploader('tests/files/hello_world.txt', chunk_size=200)
        uploader.upload()
        assert uploader.request.status_code == 204
