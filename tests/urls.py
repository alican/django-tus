from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from django_tus.views import TusUpload

urlpatterns = [
    url(r'^upload/$', TusUpload.as_view(), name='tus_upload'),
    url(r'^upload/(?P<resource_id>[0-9a-z-]+)$', TusUpload.as_view(), name='tus_upload_chunks'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
