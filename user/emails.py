from templated_mail.mail import BaseEmailMessage


class UserActivationEmail(BaseEmailMessage):
    template_name = "user/email/user_activation.html"


class UserActivationConfirmationEmail(BaseEmailMessage):
    template_name = "user/email/user_activation_confirmation.html"
