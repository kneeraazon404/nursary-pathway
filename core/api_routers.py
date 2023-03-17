from buyer_app import urls as buyer_urls
from meta import urls as meta_urls
from product import urls as product_urls
from rest_framework.routers import DefaultRouter
from user import urls as user_urls
from geouser import urls as geouser_urls

from notification import urls as notification_urls

from . import urls as core_urls

app_name = "api_routers"

routers = DefaultRouter()

# * Always extend urls after registry. If you register urls before registry, it will now be available in browsable api
# Extend router's registry
routers.registry.extend(core_urls.router.registry)
routers.registry.extend(product_urls.router.registry)
routers.registry.extend(user_urls.router.registry)
routers.registry.extend(meta_urls.router.registry)
routers.registry.extend(buyer_urls.router.registry)
routers.registry.extend(notification_urls.router.registry)
routers.registry.extend(geouser_urls.router.registry)


# Extend Router's urls
routers.urls.extend(core_urls.router.urls)
routers.urls.extend(product_urls.router.urls)
routers.urls.extend(user_urls.router.urls)
routers.urls.extend(meta_urls.router.urls)
routers.urls.extend(buyer_urls.router.urls)
routers.urls.extend(notification_urls.router.urls)
routers.urls.extend(geouser_urls.router.urls)

urlpatterns = routers.urls
