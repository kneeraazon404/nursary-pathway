from django.db.models import base
from notification.models import Notice
from .views import NoticeViewSet
from rest_framework.routers import SimpleRouter


router = SimpleRouter()

router.register("notice", NoticeViewSet, basename="notice")

urlpatterns = []
router.urls.extend(urlpatterns)
