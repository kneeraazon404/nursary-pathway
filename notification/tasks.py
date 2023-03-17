from datetime import time

from celery import shared_task
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification
from utils.logger import logger


@shared_task
def send_notification(title, message, data, type, user_id=None):
    try:
        data["type"] = type
        data["click_action"] = type
        trader_user = get_object_or_404(get_user_model(), pk=user_id)
        device = FCMDevice.objects.filter(user=trader_user).first()
        request = data["request"]
        _image = static("image/geokrishi_marketplace.png")
        _image_path = request.build_absolute_uri("/") + _image.strip("/")
        data.pop("request")
        result = device.send_message(
            Message(
                notification=Notification(
                    title=title,
                    body=message,
                    # image=_image_path,
                    image="https://www.samuhikbazar.com/static/img/geokrishi_marketplace.ff766e09.png",
                ),
                data=data,
            )
        )
        return result
    except Exception as e:
        logger.exception(e)
        pass


@shared_task
def test():
    for i in range(100):
        time.sleep(10)
        print(f"TASK{i} Completed")
