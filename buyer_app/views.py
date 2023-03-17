from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from utils.constants import UserType
from utils.pagination import CustomPageNumberPagination
from rolepermissions.roles import get_user_roles
from notification.models import Notice
from notification.tasks import send_notification

# from utils.permissions import IsUserType
from django.shortcuts import get_object_or_404
from buyer_app.models import ContactUs, Order, Quotation
from buyer_app.serializers import (
    ContactUsSerializer,
    OrderSerializer,
    QuotationSerializer,
)
from buyer_app.tasks import (
    contact_us,
    place_order,
    request_quotation,
    order_status_change,
)


class PlaceOrderViewSet(ModelViewSet):
    """
    API for placing order and listing all order's.
    Takes 'buyer', 'product__title', 'product__auth_user' as query_params for filtration
    """

    queryset = Order.objects.select_related("buyer", "product_title")
    serializer_class = OrderSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = [
        "buyer",
        "product_title",
    ]

    # def get_permissions(self):
    #     if self.action == "create":
    #         self.permission_classes = [IsUserType]
    #         self.allowed_user_types = [UserType.BUYER]
    #     return super().get_permissions()

    def get_queryset(self):
        _queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser:
            _queryset = _queryset.filter(buyer=user)
        return _queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = super().create(request, *args, **kwargs)
        response.data.update({"notify_user": "You've successfully placed an Order"})
        if response.status_code == status.HTTP_201_CREATED:
            context = dict()
            site = get_current_site(request)

            context.update(
                {
                    "buyer": request.user.id,
                    "domain": site.domain,
                    "site_name": site.name,
                    "protocol": "https" if request.is_secure() else "http",
                    "product_id": response.data["product_title"],
                    "product_name": response.data["extra_info"]["product_detail"][
                        "product_name"
                    ],
                    "product_category": response.data["extra_info"]["product_detail"][
                        "product_category"
                    ],
                    "quantity": response.data["quantity"],
                    # "product_image": response.data["product_detail"]["product_img"],
                    "description": request.data["description"],
                    "offer": request.data["offer"],
                }
            )
            place_order.delay(request.user.id, context)
        return response

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        _order_id = response.data["id"]
        _product = response.data["product_detail"]["title_name"]
        _status = response.data["status"]
        if _status == Order.OrderStatus.PROCESSING:
            _status = "Processed"
        if response.status_code == status.HTTP_200_OK:
            roles = [role.get_name() for role in get_user_roles(request.user)]
            site = get_current_site(request)
            if UserType.ADMIN in roles:
                context = {
                    "domain": site.domain,
                    "site_name": site.name,
                    "protocol": "https" if request.is_secure() else "http",
                }
                order_status_change.delay(_order_id, context)
                _buyer = get_object_or_404(Order, pk=_order_id).buyer

                notification_title = "Order status updated"
                notice_title = f"You're order for {_product} is being {_status}"
                Notice.objects.create(
                    notice=notice_title,
                    type=Notice.Type.SINGLE,
                    single_user_send=_buyer,
                    redirect_data={},
                )
                send_notification(
                    title=notification_title,
                    message=notice_title,
                    data={"request": request},
                    type="Order Status",
                    user_id=_buyer.id,
                )
        return response


class RequestQuotationViewSet(GenericViewSet, CreateModelMixin, ListModelMixin):
    """
    API for requesting quotation and listing all quotations's.
    Takes 'buyer', 'product__title', 'product__auth_user' as query_params for filtration
    """

    queryset = Quotation.objects.all()
    serializer_class = QuotationSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ["buyer", "product__title", "product__auth_user"]

    # def get_permissions(self):
    #     if self.action == "create":
    #         self.permission_classes = [IsUserType]
    #         self.allowed_user_types = [UserType.BUYER]
    #     return super().get_permissions()

    def get_queryset(self):
        _queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and not user.is_superuser:
            #     # if (
            #     #     hasattr(user, "companyusers")
            #     #     # and user.companyusers.role == UserType.BUYER
            #     # ):
            _queryset = _queryset.filter(buyer=user)
        return _queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = super().create(request, *args, **kwargs)
        response.data.update({"notify_user": "You've successfully requested Quotation"})
        if response.status_code == status.HTTP_201_CREATED:
            context = dict()
            site = get_current_site(request)

            context.update(
                {
                    "buyer": request.user.id,
                    "domain": site.domain,
                    "site_name": site.name,
                    "protocol": "https" if request.is_secure() else "http",
                    "product_id": response.data["product"],
                    "product_name": response.data["product_detail"]["title_name"],
                    "product_category": response.data["product_detail"][
                        "category_name"
                    ],
                    "quantity": response.data["quantity"],
                    "product_image": response.data["product_detail"]["product_img"],
                    "description": request.data["description"],
                    "estimated_delivery_date": request.data["estimated_delivery_date"],
                }
            )
            request_quotation.delay(request.user.id, context)
        return response

    def perform_create(self, serializer):
        serializer.save(buyer=self.request.user)


class ContactUsViewSet(GenericViewSet, CreateModelMixin):
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        context = serializer.data
        site = get_current_site(self.request)
        context.update(
            {
                "domain": site.domain,
                "site_name": site.name,
                "protocol": "https" if self.request.is_secure() else "http",
            }
        )
        contact_us.delay(context)
        return instance
