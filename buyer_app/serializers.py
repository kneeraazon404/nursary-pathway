from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from product.models import Product
from product.serializers import ProductSerializer
from .models import ContactUs, Order, Quotation
from django.db.models.expressions import F


class OrderSerializer(ModelSerializer):
    buyer = PrimaryKeyRelatedField(read_only=True)
    extra_info = SerializerMethodField()

    def get_extra_info(self, instance):
        _dict = {
            "buyer_info": {
                "buyer_name": instance.buyer.trader.company_name
                if (
                    instance.buyer
                    and hasattr(instance.buyer, "trader")
                    and hasattr(instance.buyer.trader, "company_name")
                )
                else instance.buyer.username,
                "contact_number": {
                    "number": instance.buyer.trader.contact_number
                    if (
                        instance.buyer
                        and hasattr(instance.buyer, "trader")
                        and hasattr(instance.buyer.trader, "contact_number")
                    )
                    else None,
                    "mobile_number": instance.buyer.trader.mobile_number
                    if (
                        instance.buyer
                        and hasattr(instance.buyer, "trader")
                        and hasattr(instance.buyer.trader, "mobile_number")
                    )
                    else None,
                },
            },
            "product_detail": {
                "product_id": instance.product_title.product_title.first().id,
                "product_name": instance.product_title.title,
                "product_category": instance.product_title.category.get_complete_category_name,
            },
        }

        seller_list = (
            instance.product_title.product_title.filter(
                is_approved=True,
                is_deleted=False,
                status=Product.ProductStatus.APPROVED,
            )
            .annotate(
                seller_id=F("auth_user_id"),
                seller_name=F("auth_user__username"),
                seller_company=F("auth_user__trader__company_name"),
                seller_company_number=F("auth_user__trader__contact_number"),
                seller_company_mobile_number=F("auth_user__trader__mobile_number"),
                seller_province=F("auth_user__profile__province__name"),
                seller_district=F("auth_user__profile__district__name"),
                seller_palika=F("auth_user__profile__palika__name"),
                seller_ward=F("auth_user__profile__ward"),
                seller_tole=F("auth_user__profile__tole"),
                seller_quantity=F("quantity"),
                seller_price=F("price"),
            )
            .order_by("seller_id")
            .distinct("seller_id")
        )

        _dict["seller_info"] = [
            {
                "seller_id": seller.seller_id,
                "seller_name": seller.seller_name,
                "seller_company_name": seller.seller_company,
                "contact_number": {
                    "number": seller.seller_company_number,
                    "mobile_number": seller.seller_company_mobile_number,
                },
                "address": {
                    "province": seller.seller_province,
                    "district": seller.seller_district,
                    "palika": seller.seller_palika,
                    "ward": seller.seller_ward,
                    "tole": seller.seller_tole,
                },
                "quantity": seller.seller_quantity,
                "price": seller.seller_price,
            }
            for seller in seller_list
        ]

        return _dict

    class Meta:
        model = Order
        fields = [
            "id",
            "buyer",
            "product_title",
            "address",
            "quantity",
            "description",
            "offer",
            "status",
            "remarks",
            "extra_info",
            "created_at",
            "updated_at",
        ]


class QuotationSerializer(ModelSerializer):
    buyer = PrimaryKeyRelatedField(read_only=True)
    buyer_name = SerializerMethodField()
    product_detail = SerializerMethodField()
    contact_number = PrimaryKeyRelatedField(
        source="buyer.trader.contact_number", read_only=True
    )

    def get_buyer_name(self, instance):
        return instance.buyer.username

    def get_product_detail(self, instance):
        return ProductSerializer(instance.product).data

    class Meta:
        model = Quotation
        fields = [
            "id",
            "buyer",
            "buyer_name",
            "contact_number",
            "product",
            "product_detail",
            "address",
            "quantity",
            "description",
            "estimated_delivery_date",
            "created_at",
            "updated_at",
        ]


class ContactUsSerializer(ModelSerializer):
    class Meta:
        model = ContactUs
        fields = [
            "name",
            "email",
            "message",
        ]
