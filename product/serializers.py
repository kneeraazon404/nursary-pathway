from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Min, Max, Sum
from rest_framework.serializers import ModelSerializer
from drf_writable_nested.serializers import WritableNestedModelSerializer
from .models import Product, ProductImage, ProductHistory, Category, ProductTitle
from versatileimagefield.serializers import VersatileImageFieldSerializer


class EmptySerializer(serializers.Serializer):
    pass


class ProductImageSerializer(ModelSerializer):
    """
    Note: name of 'VersatileImageFieldSerializer' should be same as that of 'VersatileImageField'
    in this case that is ***image***.
    """

    image = VersatileImageFieldSerializer(sizes="headshot")

    class Meta:
        model = ProductImage
        fields = ["id", "product", "image", "featured", "is_active"]
        extra_kwargs = {"product": {"required": False}}


class CategorySerializer(ModelSerializer):
    """
    Nest Subcategories inside parent Category by help of get_fields
    method
    """

    parent_name = serializers.PrimaryKeyRelatedField(
        source="parent.title", read_only=True
    )
    slug = serializers.PrimaryKeyRelatedField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)

    def get_category_name(self, instance) -> str:
        return instance.get_complete_category_name

    class Meta:
        model = Category
        fields = [
            "id",
            "parent",
            "parent_name",
            "title",
            "slug",
            "category_name",
            "image",
            "created_at",
            "updated_at",
        ]

    def get_fields(self):
        fields = super(CategorySerializer, self).get_fields()
        fields["children"] = CategorySerializer(many=True, required=False)
        return fields


class ProductListSerializer(WritableNestedModelSerializer):
    """
    This serializer is for listing all Products in table
    """

    title_name = serializers.PrimaryKeyRelatedField(
        source="title.title", read_only=True
    )
    seller_name = serializers.PrimaryKeyRelatedField(
        source="auth_user.trader.auth_user.username", read_only=True
    )
    seller_company_name = serializers.PrimaryKeyRelatedField(
        source="auth_user.trader.company_name", read_only=True
    )
    unit_name = serializers.PrimaryKeyRelatedField(source="title.unit", read_only=True)
    category_name = serializers.SerializerMethodField()

    def get_category_name(self, instance) -> str or None:
        try:
            if instance.title:
                return instance.title.category.get_complete_category_name
        except Exception as e:
            return None

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "title_name",
            "quantity",
            "price",
            "description",
            "unit_name",
            "status",
            "auth_user",
            "seller_name",
            "seller_company_name",
            "category_name",
            "created_at",
            "updated_at",
        ]


class ProductSerializer(WritableNestedModelSerializer):
    auth_user = serializers.HiddenField(
        default=serializers.CreateOnlyDefault(serializers.CurrentUserDefault())
    )
    product_img = ProductImageSerializer(many=True, required=False)

    title_name = serializers.PrimaryKeyRelatedField(
        source="title.title", read_only=True
    )

    seller_name = serializers.PrimaryKeyRelatedField(
        source="auth_user.trader.auth_user.username", read_only=True
    )

    seller_company_name = serializers.PrimaryKeyRelatedField(
        source="auth_user.trader.company_name", read_only=True
    )

    auth_id = serializers.PrimaryKeyRelatedField(source="auth_user_id", read_only=True)

    slug = serializers.PrimaryKeyRelatedField(read_only=True)

    unit_name = serializers.PrimaryKeyRelatedField(source="title.unit", read_only=True)

    # #####################################
    # # Used if supplier sends title of product in string instead of id.
    # # If title is in string then it means new ProductTitle is to be created.
    # # So we take string title and this category to create new ProductTitle. Else,
    # # this field is not needed
    # category = serializers.IntegerField(required=False)
    # subcategory = serializers.IntegerField(required=False)
    # ######################################

    ############
    ## Only for GET/READ
    category_json = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField(read_only=True)
    category_slug = serializers.SerializerMethodField(read_only=True)
    ############

    def get_category_json(self, instance) -> dict:
        try:
            if instance.title.category and instance.title.category.parent:
                return {
                    "category_id": instance.title.category.parent_id,
                    "category_name": instance.title.category.parent.title,
                    "sub_category_id": instance.title.category_id,
                    "sub_category_name": instance.title.category.title,
                }

            elif instance.title.category and instance.title.category.parent == None:
                return {
                    "category_id": instance.title.category_id,
                    "category_name": instance.title.category.title,
                    "sub_category_id": None,
                    "sub_category_name": None,
                }
        except Exception as e:
            return {}

    def get_category_name(self, instance) -> str or None:
        try:
            if instance.title:
                return instance.title.category.get_complete_category_name
        except Exception as e:
            return None

    def get_category_slug(self, instance) -> str or None:
        try:
            if instance.title:
                return instance.title.category.slug
        except Exception as e:
            return None

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "title_name",
            "quantity",
            "price",
            "unit_name",
            "description",
            "auth_user",
            "slug",
            "status",
            "is_approved",
            "auth_id",
            "seller_name",
            "seller_company_name",
            "category_json",
            "category_name",
            "category_slug",
            "created_at",
            "updated_at",
            "product_img",
        ]

    # def create(self, validated_data):
    #     """
    #     Create product by checking existence of ProductTitle.
    #     If not and category and title_string is provided then create
    #     ProductTitle first and use it to create Product.
    #     """
    #     try:
    #         category_id = validated_data.pop("category", None)
    #         sub_category_id = validated_data.pop("subcategory", None)
    #     if (
    #         validated_data["title"] == None
    #         and validated_data["title_string"]
    #         and sub_category_id
    #     ):
    #         cat_instance = get_object_or_404(Category, id=sub_category_id)
    #         product_title = ProductTitle.objects.create(
    #             title=validated_data["title_string"],
    #             category=cat_instance,
    #         )
    #         validated_data["title"] = product_title
    #     return super().create(validated_data)
    # except Exception as e:
    #     print(e)

    def update(self, instance, validated_data):
        """
        Creating History of product on every update
        """
        ph = ProductHistory.objects.create(
            product=instance,
            title=instance.title.title,
            price=instance.price,
            quantity=instance.quantity,
        )
        if instance.description:
            ph.description = instance.description
        if instance.title.category:
            ph.category = instance.title.category.get_complete_category_name

        ph.save()

        return super().update(instance, validated_data)


class ProductHistorySerializer(ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)

    def get_created_by(self, instance) -> dict:
        obj = {
            "owner_id": instance.product.auth_user_id,
            "owner_name": instance.product.auth_user.username,
            "owner_company": instance.product.auth_user.trader.company_name,
        }
        return obj

    class Meta:
        model = ProductHistory
        fields = [
            "id",
            "title",
            "price",
            "description",
            "category",
            "product",
            "quantity",
            "created_by",
            "created_at",
        ]


class ProductTitleSerializer(ModelSerializer):
    """
    Serializer for showing products in particular category
    """

    category_name = serializers.SerializerMethodField(read_only=True)

    def get_category_name(self, instance):
        return instance.category.get_complete_category_name

    class Meta:
        model = ProductTitle
        fields = [
            "id",
            "title",
            "category",
            "category_name",
            "unit",
            "is_active",
        ]


class UniqueProductSerializer(ProductSerializer):
    cost_quantity = serializers.SerializerMethodField()

    def get_cost_quantity(self, instance):
        product_id = instance.title.id
        info = Product.objects.filter(
            title=product_id,
            is_approved=True,
            is_deleted=False,
            status=Product.ProductStatus.APPROVED,
        ).aggregate(Max("price"), Min("price"), Sum("quantity"))
        return {
            "max_price": info["price__max"],
            "min_price": info["price__min"],
            "total_quantity": info["quantity__sum"],
        }

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ["cost_quantity"]


class SimpleUniqueProductSerializer(ModelSerializer):
    """
    Simple Serializer that returns only id, title, title_name of unique product
    """

    title_name = serializers.PrimaryKeyRelatedField(
        source="title.title", read_only=True
    )

    class Meta:
        model = Product
        fields = ["id", "title", "title_name"]


class ProductDetailSerializer(UniqueProductSerializer):
    """
    Serializer for viewing detail of a product
    """

    # similar_products = serializers.SerializerMethodField()

    # def get_similar_products(self, instance):
    #     ## We cannot access request in serializer. So, from context acsessing request.
    #     _request = self.context["request"]
    #     qs = Product.objects.filter(
    #         title=instance.title.id,
    #         title__category=instance.title.category.id,
    #         is_approved=True,
    #     ).exclude(pk=instance.id)
    #     return UniqueProductSerializer(
    #         qs, context={"request": _request}, many=True
    #     ).data

    class Meta(UniqueProductSerializer.Meta):
        fields = UniqueProductSerializer.Meta.fields
