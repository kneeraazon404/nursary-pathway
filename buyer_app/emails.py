from templated_mail.mail import BaseEmailMessage


class PlaceOrderEmail(BaseEmailMessage):
    template_name = "buyer_app/email/place_order.html"


class OrderStatusUpdateEmail(BaseEmailMessage):
    template_name = "buyer_app/email/order_status_email.html"


class RequestQuotationEmail(BaseEmailMessage):
    template_name = "buyer_app/email/request_quotation.html"


class ContactUsEmail(BaseEmailMessage):
    template_name = "buyer_app/email/contact_us_email.html"
