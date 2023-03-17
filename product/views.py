from django.db.models.expressions import Subquery, OuterRef
from utils.constants import UserType
from rest_framework import mixins, filters, status
from utils.filters import PriceRangeFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from utils.serializers import TotalSerializer, EmptySerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from utils.pagination import CustomPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from drf_writable_nested.serializers import WritableNestedModelSerializer

from .models import Product, ProductHistory, Category, ProductImage, ProductTitle
from .serializers import (
    ProductSerializer,
    ProductListSerializer,
    ProductImageSerializer,
    ProductDetailSerializer,
    ProductTitleSerializer,
    UniqueProductSerializer,
    SimpleUniqueProductSerializer,
    ProductHistorySerializer,
    CategorySerializer,
)
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope

from django.db.models import Prefetch
from utils.permissions import IsUserType
from notification.models import Notice
from notification.tasks import send_notification

# Create your views here.

"""
At the moment one vendor cannot see products of other vendors
"""


class ProductView(ModelViewSet):
    # permission_classes = [AllowAny, TokenHasScope]

    serializer_class = ProductSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = [
        PriceRangeFilter,
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "price",
        "auth_user",
        "title__category",
        "quantity",
        "title__category__slug",
    ]
    search_fields = ["title__title"]
    ordering_fields = ["id", "title__title", "price"]

    def get_serializer(self, *args, **kwargs):
        if self.action == "product_delete":
            return EmptySerializer
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        request = self.request
        _queryset = Product.objects.filter(
            is_deleted=False
        ).select_related(  # ,auth_user=request.user.id
            "auth_user",
            "title__category",
            "title__category__parent",
            "auth_user__trader",
            "auth_user__profile",
        )
        if self.action in [
            "all_product_detail",
            "total_product_count",
        ]:
            """
            If user is admin show all product's detail, i.e. even if product is not approved.
            """
            _queryset = _queryset
        elif self.action in [
            "unique_product",
            "other_suppliers_product_list",
            "all_unique_product_list",
        ]:
            """
            Especially for buyer to show product which are approved and aggregated
            """
            _queryset = (
                _queryset.filter(
                    is_approved=True, status=Product.ProductStatus.APPROVED
                )
                .order_by("title__title")
                .distinct("title__title")
            )
        elif self.action == "all_product_list":
            """
            For admin to show list of all aggregated product
            """
            ids = (
                _queryset.distinct("title__title", "auth_user")
                .order_by("title__title", "auth_user", "-updated_at")
                .values_list("id", flat=True)
            )
            _queryset = _queryset.filter(id__in=ids).order_by("-updated_at")
        else:
            """
            If user is SuperUser show all Product.
            If user is vendor show only his/her product
            """
            if (
                request.user
                and request.user.is_authenticated
                and request.user.is_superuser
            ):
                _queryset = _queryset
        return _queryset

    def get_permissions(self):
        if self.action in [
            "all_product_list",
            "all_product_detail",
            "total_product_count",
        ]:
            self.permission_classes = [AllowAny]
            # self.allowed_user_types = [UserType.ADMIN]
        elif self.action == "create":
            self.permission_classes = [IsUserType]
            self.allowed_user_types = [UserType.VENDOR]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        # if request.data["title"] == "0" or request.data["title"] == 0:
        #     request.data["title"] = None
        response = super().create(request, *args, **kwargs)
        response.data.update(
            {
                "notify_user": "Product submission successful. Product shall be reviewed by admin for approval"
            }
        )
        return response

    def update(self, request, *args, **kwargs):
        """
        Change 'is_approved' field to False if updated by vendor(owner).
        Change 'is_approved' to True if updated by ADMIN.
        """
        partial = True
        instance = self.get_object()
        is_vendor = request.user.groups.filter(name=UserType.VENDOR).exists()
        if is_vendor == True and request.user == instance.auth_user:
            instance.is_approved = False
            instance.status = Product.ProductStatus.PENDING
        instance.save()
        response = super().update(request, *args, **kwargs)
        if is_vendor:
            response.data.update(
                {
                    "notify_user": "You've successfully updated a product. Changes shall be reviewed by admin for approval"
                }
            )
        if request.user.is_superuser:
            status = response.data["status"]
            notification_title = "Product status updated"
            notice_title = f"You're product '{instance.title.title}' has been {status}"
            Notice.objects.create(
                notice=notice_title,
                type=Notice.Type.SINGLE,
                single_user_send=instance.auth_user,
                redirect_data={},
            )
            send_notification(
                title=notification_title,
                message=notice_title,
                data={"request": request},
                type="Product Status",
                user_id=instance.auth_user.id,
            )

        return response

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProductDetailSerializer(instance, context={"request": request})
        return Response(serializer.data)

    @action(detail=False)
    def all_product_list(self, request, *args, **kwargs):
        """
        All Products List For Admin User.

        Note: Action method doesnot filter and paginate by default
            if not called super().
        So, add pagination code and use self.filter_queryset() to wrap
            self.get_queryset() for it.
        """
        try:
            if request.user and (
                request.user.is_superuser
                or (
                    request.user.profile
                    and request.user.groups.filter(name=UserType.ADMIN).exists()
                )
            ):
                queryset = self.get_queryset()
            else:
                return Response({"Nothing to Show"})
        except Exception as e:
            return Response({"Nothing to Show"})

        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        return Response(
            ProductListSerializer(
                queryset, context={"request": request}, many=True
            ).data
        )

    @action(detail=False)
    def other_suppliers_product_list(self, request, *args, **kwargs):
        """
        An API for supplier to buy product. This api is same as
        unique_product but with pagination.
        """
        if request.user.groups.filter(name=UserType.BUYER).exists():
            queryset = (
                self.get_queryset()
                .exclude(auth_user=request.user)
                .filter(
                    title__category__parent__in=request.user.trader.category_associated_with.all()
                )
                .prefetch_related(
                    Prefetch(
                        "product_img",
                        queryset=ProductImage.objects.filter(
                            featured=True, is_active=True
                        ),
                    )
                )
            )
        else:
            return Response({"Error": "Nothing Found"})
        product_list = self.filter_queryset(queryset)
        product_qs = product_list

        page = self.paginate_queryset(product_qs)

        if page is not None:
            serializer = UniqueProductSerializer(
                page, context={"request": request}, many=True
            )
            return self.get_paginated_response(serializer.data)

        return Response(
            UniqueProductSerializer(
                product_qs, context={"request": request}, many=True
            ).data
        )

    @action(detail=True)
    def all_product_detail(self, request, *args, **kwargs):
        """
        All Products Detail For Admin User
        """
        if (
            request.user.is_superuser
            or request.user.groups.filter(name=UserType.ADMIN).exists()
        ):
            return super(ProductView, self).retrieve(request, *args, **kwargs)
        else:
            return Response()

    @action(detail=False)
    def total_product_count(self, request, *args, **kwargs):
        """
        Gives total active(not deleted) product counts
        """
        total = self.get_queryset().count()
        data = {"total": total}
        return Response(TotalSerializer(data).data)

    @action(detail=False, url_path="product_detail_by_slug/(?P<slug>[^/.]+)")
    def product_detail_by_slug(self, request, *args, **kwargs):
        """
        Modified url path to use slug.
        @action gives way to change/customize url_path.
        Add context in response to get full url of product_image.
        """
        _slug = self.kwargs["slug"]
        obj = get_object_or_404(Product, slug=_slug)
        return Response(ProductSerializer(obj, context={"request": request}).data)

    @action(detail=False)
    def unique_product(self, request, *args, **kwargs):
        """
        This method gives unique Product with max and min price from all
        related products. Eg: if we have 10 apples of different price then
        this gives info(description, title, category) of single(first) apple with
        additional data i.e.max and min price from those 10 apples.

        Run this API to know about json data it gives.
        """

        """
        This also works if you don't want to calculate min/max in
        serializer.

        Product.objects.values('title__title')
        .annotate(min_val=Min('price'), max_val=Max('price'))
        .order_by("title__title")
        """

        """
        Note: Action method doesnot filter and paginate by default
            if not called super().
        So, add pagination code and use self.filter_queryset() to wrap
            self.get_queryset() for it.
        """

        queryset = self.get_queryset()
        product_list = self.filter_queryset(queryset)
        return Response(
            UniqueProductSerializer(
                product_list, context={"request": request}, many=True
            ).data
        )

    @action(detail=False)
    def all_unique_product_list(self, request, *args, **kwargs):
        """
        This method is same as unique_product but only returns (id, product and product_name)
        """
        _queryset = self.get_queryset().only("id", "title", "auth_user")
        return Response(SimpleUniqueProductSerializer(_queryset, many=True).data)

    @action(methods=["patch"], detail=True)
    def product_delete(self, request, *args, **kwargs):
        """
        Soft delete product
        """
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        if instance.is_deleted:
            return Response({"result": "Product already deleted"})
        else:
            try:
                instance.soft_delete()
                return Response({"result": "deleted"})
            except Exception as e:
                # Todo: Use Logger to see error during deletion of product
                return Response({"result": "Not deleted"})


class ProductHistoryViewSet(mixins.ListModelMixin, GenericViewSet):
    serializer_class = ProductHistorySerializer
    queryset = ProductHistory.objects.select_related(
        "product", "product__auth_user", "product__auth_user__trader"
    ).order_by("-id")
    pagination_class = CustomPageNumberPagination
    # permission_classes = [IsUserType]
    # allowed_user_types = [UserType.ADMIN]

    def get_queryset(self):
        if self.action == "particular_product_history":
            product_title = self.request.query_params.get("title", None)
            product_owner = self.request.query_params.get("owner", None)

            queryset = self.queryset.filter(
                product__title=product_title, product__auth_user=product_owner
            ).order_by("-id")
            return queryset
        return super().get_queryset()

    @action(detail=False)
    def particular_product_history(self, request, *args, **kwargs):
        """
        API for history of particular product.
        Takes 'title' and 'owner' as query_params.
        """
        return super(ProductHistoryViewSet, self).list(request, *args, **kwargs)


class ProductTitleViewSet(ModelViewSet):
    """
    API for listing all products alongwith it's category.
    Takes 'category' as query_params for filtering on basis of category.
    """

    serializer_class = ProductTitleSerializer
    filterset_fields = ["category"]

    def get_queryset(self):
        queryset = ProductTitle.objects.select_related("category")
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            queryset = queryset.filter(is_active=True)
        return queryset

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            request.data["is_active"] = True
        return super().create(request, *args, **kwargs)

    @action(detail=False)
    def check_product_title_existance(self, request, *args, **kwargs):
        """
        Checks if product_title exists and returns product_title_id as response accordingly.
        """
        product_id = request.query_params.get("product_id", None)
        product = Product.objects.filter(id=product_id).annotate(
            title_exists=Subquery(
                ProductTitle.objects.filter(
                    title__exact=OuterRef("title__title"), is_active=False
                ).values("id")[:1]
            ),
        )
        result = {"exists": product.first().title_exists}
        return Response(result)

    @action(detail=False)
    def activate_product_title(self, request, *args, **kwargs):
        """
        Activate product_title
        """
        product_title_id = request.query_params.get("product_title_id", None)
        product_title = get_object_or_404(ProductTitle, pk=product_title_id)
        if product_title and hasattr(product_title, "is_active"):
            product_title.is_active = True
            product_title.save()
            return Response({"product_title_status": "Active"})
        return Response({"error": "Error during activation of product_title"})


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.select_related("product")

    @action(detail=False)
    def update_images_on_bulk(self, request, *args, **kwargs):
        """
        API for updating images on bulk.
        @params: image_id
        """
        images_id_str = request.query_params.get("image_id").split(",")
        images_id_int = list(map(int, images_id_str))
        update_images = (
            self.get_queryset()
            .filter(id__in=images_id_int)
            .update(featured=True, is_active=True)
        )
        return Response({"result": "Images updated"}, status=status.HTTP_200_OK)


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.select_related("parent").order_by("-updated_at")
    permission_classes = [AllowAny]

    @action(detail=False)
    def category_for_mobile(self, request, *args, **kwargs):
        """
        API for nesting subcategories inside a category like Tree structure.
        Doesnot take any params.

        For Backend only:
            Filter by parent as None for not repeating Subcategories in response
            as they are already nested inside their respective Category.
        """
        _queryset = self.get_queryset().filter(parent=None)
        return Response(
            CategorySerializer(_queryset, many=True, context={"request": request}).data
        )
