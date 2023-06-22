from django.urls import reverse

from tusclient.client import TusClient


class TestUploadView:
    def test_get_is_not_allowed(self, client):
        response = client.get(reverse("tus_upload"))
        assert response.status_code == 405

    def test_upload_file(self, live_server):
        tus_client = TusClient(
            live_server.url + reverse("tus_upload"),
        )
        uploader = tus_client.uploader("tests/files/hello_world.txt", chunk_size=200)
        uploader.upload()
        assert uploader.request.status_code == 204
