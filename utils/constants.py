from django.db import models
from django.utils.translation import ugettext_lazy as _


class UserType(models.TextChoices):
    BUYER = "buyer", "buyer"
    VENDOR = "vendor", "vendor"
    ADMIN = "admin", "admin"


PRODUCT_ADDED = _("उत्पादन बिक्रिको लागि सफलतापुर्वक थपियो।")
PRODUCT_UPDATED = _("उत्पादनको डाटा सफलतापुर्वक अपडेट भयो।")
PRODUCT_DELETED = _("उत्पादन सफलतापुर्वक हटाइयो। ")
AVAILABLE_DATE_FROM_TODAY = _("कृपया उत्पादन मिति आज बाट हाल्नु होला|")
ENGLISH_DATE_REQUIRED = _("Please provide english date")
PRODUCT_EXPIRED = _("तपाईको उत्पादन को म्याद सकियो।  ")
PRODUCT_SOLD = _("तपाईको उत्पादन सफलतापुर्वक बिक्रि भयो। ")
PRODUCT_CANCELED = _("तपाईको उत्पादन सफलतापुर्वक cancel भयो। ")
