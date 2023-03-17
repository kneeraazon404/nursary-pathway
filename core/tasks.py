from celery import shared_task


@shared_task
def mobile_reset_password(user_id, context):
    from .tasks_logic import mobile_reset_password

    return mobile_reset_password(user_id, context)


@shared_task
def confirm_password_change(user_id, context):
    from .tasks_logic import confirm_password_change

    return confirm_password_change(user_id, context)
