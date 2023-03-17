from django.contrib.auth import get_user_model
from user.models import AdminEmail
from utils.constants import UserType
from .emails import (
    ContactUsEmail,
    PlaceOrderEmail,
    RequestQuotationEmail,
    OrderStatusUpdateEmail,
)
from .models import Order, Quotation
from django.shortcuts import get_object_or_404

USER = get_user_model()


def place_order(user_id, context):
    buyer = USER.objects.get(id=user_id)
    # _email = AdminEmail.objects.filter(is_active=True).values_list("email", flat=True)
    to = list(AdminEmail.objects.filter(is_active=True).values_list("email", flat=True))
    context.update(
        {
            "buyer": buyer,
            "buyer_email": buyer.email,
            "buyer_company_name": buyer.trader.company_name,
            "buyer_contact_person": buyer.trader.contact_person,
            "buyer_contact_number": buyer.trader.contact_number
            if buyer.trader.contact_number
            else buyer.trader.mobile_number,
        }
    )
    try:
        email = PlaceOrderEmail(context=context)
        email.send(to)
    except Exception as e:
        print("Exception: ", e)


def order_status_change(order_id, context):
    order_obj = get_object_or_404(Order, pk=order_id)
    product_name = order_obj.product.title.title
    product_category = order_obj.product.title.category
    buyer_name = order_obj.buyer.username
    quantity = order_obj.quantity
    status = order_obj.status
    offered_price = order_obj.offer
    total_cost = order_obj.quantity * order_obj.offer
    remarks = order_obj.remarks

    context.update(
        {
            "product_name": product_name,
            "product_category": product_category,
            "buyer_name": buyer_name,
            "quantity": quantity,
            "status": status,
            "total_cost": total_cost,
            "offered_price": offered_price,
            "remarks": remarks,
        }
    )

    to = [order_obj.buyer.email]
    try:
        email = OrderStatusUpdateEmail(context=context)
        email.send(to)
    except Exception as e:
        print("Exception from order_status_update email: ", e)


def request_quotation(user_id, context):
    buyer = USER.objects.get(id=context["buyer"])
    # _email = AdminEmail.objects.filter(is_active=True).values_list("email", flat=True)
    to = list(AdminEmail.objects.filter(is_active=True).values_list("email", flat=True))
    context.update(
        {
            "buyer": buyer,
            "buyer_email": buyer.email,
            "buyer_company_name": buyer.trader.company_name,
            "buyer_contact_person": buyer.trader.contact_person,
            "buyer_contact_number": buyer.trader.contact_number
            if buyer.trader.contact_number
            else buyer.trader.mobile_number,
        }
    )

    try:
        email = RequestQuotationEmail(context=context)
        email.send(to)
    except Exception as e:
        print("Exception: ", e)


def contact_us(context):
    # _email = AdminEmail.objects.filter(is_active=True).values_list("email", flat=True)
    to = list(AdminEmail.objects.filter(is_active=True).values_list("email", flat=True))

    try:
        email = ContactUsEmail(context=context)
        email.send(to)
    except Exception as e:
        print("Exception: ", e)
