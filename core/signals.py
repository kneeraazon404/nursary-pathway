from core.utils import moment_text
from django.conf import settings
from django.contrib.sites.models import Site
from django.dispatch import receiver
from django_rest_resetpassword.signals import (
    post_password_reset,
    reset_password_token_created,
)
from djoser.conf import settings as djoser_settings
from .tasks import confirm_password_change, mobile_reset_password


@receiver(reset_password_token_created)
def password_reset_token_created(
    sender, instance, reset_password_token, *args, **kwargs
):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    print("Received password reset token created")

    site = Site.objects.get_current()
    context = {
        "domain": site.domain,
        "site_name": site.name,
        "user_id": reset_password_token.user.id,
        "username": reset_password_token.user.username,
        "email": reset_password_token.user.email,
        "reset_token": reset_password_token.key,
        "validity": moment_text(settings.PASSWORD_RESET_TIMEDELTA),
    }

    mobile_reset_password.delay(reset_password_token.user.id, context)


@receiver(post_password_reset)
def password_reset_completed(user, *args, **kwargs):
    """
    Handles password reset completed
    :param user: User Model Object
    :param args:
    :param kwargs:
    :return:
    """
    if djoser_settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
        site = Site.objects.get_current()
        context = {
            "domain": site.domain,
            "site_name": site.name,
        }

        confirm_password_change.delay(user.id, context)
