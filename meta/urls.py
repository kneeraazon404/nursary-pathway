from rest_framework.routers import SimpleRouter

from .views import DistrictViewSet, PalikaViewSet, ProvinceViewSet

router = SimpleRouter()
router.register("provinces", ProvinceViewSet, basename="provinces")
router.register("districts", DistrictViewSet, basename="districts")
router.register("palikas", PalikaViewSet, basename="palikas")

urlpatterns = []

router.urls.extend(urlpatterns)
