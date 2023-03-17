# from django.contrib.auth.middleware import RemoteUserMiddleware
from django.conf import settings

# class CustomMiddleware(RemoteUserMiddleware):
#     def process_request(self,request):
#         header = 'HTTP_X_USERNAME'
#         request.id = request.headers.get(request.user.id)
#             # print("middleware",request.id)Bearer
#             #
#         print("middleware",request.id)


from django.utils.deprecation import MiddlewareMixin
from django.http.response import HttpResponseForbidden
import requests
from .models import GeokrishiUsers
from .serializers import GeoUserSerializer


class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.geotoken = request.headers.get("GEOTOKEN")
        geotoken = request.geotoken
        if geotoken:
            r = requests.get(
                f"{settings.GEOKRISHI_BASE}/api/user/profile",
                headers={"Authorization": geotoken},
            )
            r_data = r.json()
            request.geouser = r_data.pop("id")
            r_data["geo_user_id"] = request.geouser
            geo = GeokrishiUsers.objects.filter(geo_user_id=request.geouser)
            if not geo.exists():
                serializer = GeoUserSerializer(data=r_data)
                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                except Exception as e:
                    print(e)
            else:
                serializer = GeoUserSerializer(instance=geo.first(), data=r_data)
                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                except Exception as e:
                    print(e)

        # GEOTOKEN = request.headers.get()

        # if not request.apptype:
        #     return HttpResponseForbidden('Please specify apptype.')

    def geo_user(geotoken):
        r = requests.get(
            f"{settings.GEOKRISHI_BASE}/api/user/profile",
            headers={"Authorization": geotoken},
        )
        r_data = r.json()
        r_data["c_id"] = r_data.pop("id")
        id_value = r_data["c_id"]
        request.geouser = id_value
        r_data["geo_user_id"] = r_data.pop("c_id")
        geo = GeokrishiUsers.objects.filter(geo_user_id=id_value)
        if geo:
            print("User already exists")
        else:
            print("No user")
            serializer = GeoUserSerializer(data=r_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return
