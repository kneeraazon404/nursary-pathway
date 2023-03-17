from rest_framework.routers import SimpleRouter

# from .views import BuyerViewSet, VendorSerializerViewSet, TraderViewSet
from .views import TraderViewSet


router = SimpleRouter()
# router.register("vendor", VendorSerializerViewSet, basename="vendor")
# router.register("buyers", BuyerViewSet, basename="buyers")
router.register("trader", TraderViewSet, basename="trader")
# router.register("access", Acess, basename="acess")
# router.register("geokrishi/user", GeoUser, basename="geouser")
# router.register("geokrishi/product", GeoProduct, basename="geoproduct")


urlpatterns = []

router.urls.extend(urlpatterns)
