from utils.constants import UserType
from rest_framework import permissions

SAFE_METHODS = ("GET", "HEAD", "OPTIONS")


class IsUserType(permissions.BasePermission):
    """
    The request is authenticated if user's user_type is in allowed_user_types.
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "groups")
        ):
            try:
                allowed_user_type = view.allowed_user_types
                user_groups_names = request.user.groups.all()
                user_type = [types.name for types in user_groups_names]
            except:
                return False
            common_user_types = set(user_type).intersection(allowed_user_type)
            if common_user_types:
                return True
        else:
            return False


class IsUserTypeOrReadOnly(permissions.BasePermission):
    """
    The request is authenticated if profile's user_type is in is_user_types_or_read_only, or is a read-only request.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or request.user.is_superuser:
            return True

        if (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
        ):
            try:
                allow_or_readOnly_user_type = view.allow_or_readOnly_user_types
                user_groups_names = request.user.groups.all()
                user_type = [types.name for types in user_groups_names]
            except:
                return False
            common_user_types = set(user_type).intersection(allow_or_readOnly_user_type)
            if common_user_types:
                return True
        else:
            return False


# class IsCreatorOrReadOnly(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         if request.method in SAFE_METHODS:
#             return True
#         if request.method in ["PUT", "PATCH", "DELETE"]:
#             obj_user = obj.auth_user
#             if (
#                 request.user
#                 and request.user.is_authenticated
#                 and hasattr(request.user, "profile")
#             ):
#                 if (
#                     obj_user == request.user
#                     and obj_user.profile.user_type == request.user.profile.user_type
#                 ):
#                     return True
#                 return False
#             return False


# class IsAdminUserOrReadOnly(permissions.BasePermission):
#     def has_permission(self, request, view):
#         if request.user.is_superuser:
#             return True
#         if (
#             request.user
#             and request.user.is_authenticated
#             and hasattr(request.user, "profile")
#         ):
#             if request.method in SAFE_METHODS and (
#                 request.user.profile.user_type == UserType.VENDOR
#             ):
#                 return True
#             elif request.method in ["POST", "PUT", "PATCH", "DELETE"] and (
#                 request.user.profile.user_type == UserType.ADMIN
#             ):
#                 return True
#             else:
#                 return False
#         else:
#             return False
