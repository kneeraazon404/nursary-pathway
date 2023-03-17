from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContactUsViewSet, PlaceOrderViewSet, RequestQuotationViewSet

router = DefaultRouter()

router.register(r"place_order", PlaceOrderViewSet, basename="place_order")
router.register(
    r"request_quotation", RequestQuotationViewSet, basename="request_quotation"
)
router.register(r"contact_us", ContactUsViewSet, basename="contact_us")

app_name = "buyer_app"
urlpatterns = [
    path("", include(router.urls)),
]
