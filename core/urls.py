from django.urls import re_path, path
from django.views.generic.base import TemplateView
from rest_framework.routers import SimpleRouter

from .views import (
    AuthView,
    MyObtainTokenPairView,
    MyTokenRefreshPairView,
    TokenClearView,
)

router = SimpleRouter()
router.register("jwt", MyObtainTokenPairView, basename="token_obtain")
router.register("jwt/refresh", MyTokenRefreshPairView, basename="token_refresh")
router.register("jwt/clear", TokenClearView, basename="token_clear")

router.register("auth", AuthView, basename="auth")

dj_rest_urls = [
    # path("auth/facebook/", FacebookLogin.as_view(), name="fb_login"),
    # path("auth/google/", GoogleLogin.as_view(), name="google_login"),
    # Required by social logins
    re_path(
        r"^account-confirm-email/(?P<key>[-:\w]+)/$",
        TemplateView.as_view(),
        name="account_confirm_email",
    ),
]

urlpatterns = [
    # path("access/samuhik", AcessView.as_view(), name="samuhik"),
]

urlpatterns += dj_rest_urls

router.urls.extend(urlpatterns)
