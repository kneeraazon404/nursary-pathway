"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.urls.conf import re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core import views as core_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("social/", include("allauth.urls")),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("core.api_routers")),
    path("robots.txt", core_views.robots, name="robots"),
    # path("geouser/", include("geouser.urls")),
    path("manifest.json", core_views.manifest, name="manifest"),
    path("service-worker.js", core_views.service_worker, name="service-worker"),
]

if settings.DEBUG:
    # API Documentation
    # Available only on debug mode
    urlpatterns += [
        # YOUR PATTERNS
        path("api/schema/", SpectacularAPIView.as_view(api_version=1.0), name="schema"),
        # Optional UI:
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
    ]

if settings.DEBUG and not settings.TESTING:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

"""
Generates a regex with reverse lookup of urls including static an>
This regex is then used in re_path of Vue's index.html.
This is done to handle any django url without a trailing slash.
"""

urls = list()
if settings.STATIC_URL:
    static_url = settings.STATIC_URL
    if static_url != "/":
        static_url = static_url.strip("/")

    urls.append(static_url)
if settings.MEDIA_URL:
    media_url = settings.MEDIA_URL
    if media_url != "/":
        media_url = media_url.strip("/")
    urls.append(media_url)
for url in urlpatterns:
    urls.append(str(url.pattern).strip("/"))
pattern_base = f'(?!{"|".join(urls)})'
pattern_index = f"^{pattern_base}.*$"
urlpatterns += [
    re_path(pattern_index, core_views.index_view, name="Home"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
