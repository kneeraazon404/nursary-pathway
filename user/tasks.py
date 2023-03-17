from celery import shared_task
from django.contrib.auth import get_user_model

from .emails import UserActivationConfirmationEmail, UserActivationEmail


@shared_task
def send_user_activation(user_id, context):
    user = get_user_model().objects.get(id=user_id)
    context.update({"user": user})
    to = [user.email]
    try:
        email = UserActivationEmail(context=context)
        email.send(to)
    except Exception as e:
        print("Exception: ", e)


@shared_task
def send_user_activation_confirmation(user_id, context):
    user = get_user_model().objects.get(id=user_id)
    context.update({"user": user})
    to = [user.email]
    try:
        email = UserActivationConfirmationEmail(context=context)
        email.send(to)
    except Exception as e:
        print("Exception: ", e)
