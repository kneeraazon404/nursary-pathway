from utils.logger import logger
from django.contrib.auth import get_user_model
from djoser.email import PasswordResetEmail, PasswordChangedConfirmationEmail
from utils.auth import get_name

USER = get_user_model()


def mobile_reset_password(user_id, context):
    user = USER.objects.get(id=user_id)
    context["user"] = user
    context["name"] = get_name(user)
    to = [user.email]
    try:
        email = PasswordResetEmail(
            context=context,
            template_name="email/mobile_password_reset.html",
        )
        email.send(to)
    except Exception as e:
        logger.exception(e)


def confirm_password_change(user_id, context):
    user = USER.objects.get(id=user_id)
    context["user"] = user
    context["name"] = get_name(user)
    to = [user.email]
    try:
        email = PasswordChangedConfirmationEmail(
            context=context,
            template_name="email/password_changed_confirmation.html",
        )
        email.send(to)
    except Exception as e:
        logger.exception(e)
