from celery import shared_task
from django.utils import timezone

from geouser.models import GeokrishiProduct


def get_local_time():
    return timezone.now().astimezone(timezone.get_current_timezone())


@shared_task
def beattask():
    today = get_local_time()
    GeokrishiProduct.objects.filter(
        available_date_eng__lt=today, status=GeokrishiProduct.AVAILABLE
    ).update(status=GeokrishiProduct.EXPIRED)
    print("Beat task executed ")


# @shared_task
# def add(x, y):
#     return x + y


# @shared_task
# def mul(x, y):
#     return x * y


# @shared_task
# def xsum(numbers):
#     return sum(numbers)


# @shared_task
# def count_widgets():
#     return Widget.objects.count()


# @shared_task
# def rename_widget(widget_id, name):
#     w = Widget.objects.get(id=widget_id)
#     w.name = name
#     w.save()
