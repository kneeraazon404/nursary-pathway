from rest_framework.routers import SimpleRouter
from .views import (
    ProductView,
    ProductHistoryViewSet,
    CategoryViewSet,
    ProductTitleViewSet,
    ProductImageViewSet,
)

router = SimpleRouter()

router.register("product", ProductView, basename="product")
router.register("product-history", ProductHistoryViewSet, basename="product_history")
router.register("category", CategoryViewSet, basename="category")
router.register("product-title", ProductTitleViewSet, basename="product-title")
router.register("product-image", ProductImageViewSet, basename="product-image")

urlpatterns = []

router.urls.extend(urlpatterns)
