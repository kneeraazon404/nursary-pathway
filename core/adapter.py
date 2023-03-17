from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from user.models import Profile

from utils.constants import UserType


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Create profile of user if profile is not present for the user
        """
        user = super().save_user(request, sociallogin, form)
        if not hasattr(user, "profile"):
            Profile.objects.create(auth_user=user, user_type=UserType.BUYER)
        return user
