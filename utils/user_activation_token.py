from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django_rest_resetpassword.models import (
    ResetPasswordToken,
    clear_expired,
    get_password_reset_token_expiry_time,
)


HTTP_USER_AGENT_HEADER = getattr(
    settings, "DJANGO_REST_RESETPASSWORD_HTTP_USER_AGENT_HEADER", "HTTP_USER_AGENT"
)
HTTP_IP_ADDRESS_HEADER = getattr(
    settings, "DJANGO_REST_RESETPASSWORD_IP_ADDRESS_HEADER", "REMOTE_ADDR"
)


def generate_token_for_user_activation(request, user):
    """
    Uses django-rest-resetpassword library for it's model and logic.
    Creates ResetPasswordToken model
    """

    # before we continue, delete all existing expired tokens
    password_reset_token_validation_time = get_password_reset_token_expiry_time()

    # datetime.now minus expiry hours
    now_minus_expiry_time = timezone.now() - timedelta(
        hours=password_reset_token_validation_time
    )

    # delete all tokens where created_at < now - 24 hours
    clear_expired(now_minus_expiry_time)

    ## check earlier token current user and delete it
    ## For resend
    ResetPasswordToken.objects.filter(user=user).delete()

    token = ResetPasswordToken.objects.create(
        user=user,
        user_agent=request.META.get(HTTP_USER_AGENT_HEADER, ""),
        ip_address=request.META.get(HTTP_IP_ADDRESS_HEADER, ""),
    )

    return token.key
