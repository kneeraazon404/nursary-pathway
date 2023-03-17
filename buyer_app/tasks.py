from config.celery import app
from django.contrib.auth import get_user_model

USER = get_user_model()

task = app.task


@task
def place_order(user_id, context):
    from .tasks_logic import place_order

    return place_order(user_id, context)


@task
def order_status_change(order_id, context):
    from .tasks_logic import order_status_change

    return order_status_change(order_id, context)


@task
def request_quotation(user_id, context):
    from .tasks_logic import request_quotation

    return request_quotation(user_id, context)


@task
def contact_us(context):
    from .tasks_logic import contact_us

    return contact_us(context)
