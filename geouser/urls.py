from rest_framework.routers import SimpleRouter
from django.urls import re_path

from .views import (
    GeoUser,
    GeoProduct,
    GeokrishiCategoryViewset,
    GeokrishiSubCategory,
    GeoItemsViewset,
    GeokrishiProxyView,
)

app_name = "geouser"


router = SimpleRouter()


urlpatterns = [
    re_path(r"geokrishi/(?P<path>.*)", GeokrishiProxyView.as_view()),
]
router.urls.extend(urlpatterns)


# router.register("geokrishi", GeokrishiView, basename="geokrishi")
# router.register("geokrishi/user", GeoUser, basename="geouser")
# router.register("geokrishi/product", GeoProduct, basename="geoproduct")
# router.register("geokrishi/items", GeoItemsViewset, basename="geoitems")

# router.register(
#     "geokrishi/category", GeokrishiCategoryViewset, basename="geokrishicategory"
# )
# router.register(
#     "geokrishi/subcategory", GeokrishiSubCategory, basename="geokrishisubcategory"
# )

urlpatterns = router.urls
