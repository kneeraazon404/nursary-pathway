from django.shortcuts import render
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from .serializers import NoticeSerializer
from .models import Notice
from django.db.models import Q
from rolepermissions.roles import get_user_roles

# Create your views here.


class NoticeViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    serializer_class = NoticeSerializer

    def get_queryset(self):
        _queryset = Notice.objects.none()
        if self.action == "list":
            if self.request.user.is_authenticated and hasattr(
                self.request.user, "profile"
            ):
                user = self.request.user
                _role_list = get_user_roles(user)
                _roles = [role.get_name() for role in _role_list]
                _queryset = Notice.objects.filter(
                    (
                        Q(type=Notice.Type.ALL)
                        | Q(group_user_send__icontains=_roles)
                        | Q(single_user_send=user.id)
                    ),
                    is_active=True,
                ).order_by("-id")
            else:
                _queryset = Notice.objects.all()
        return _queryset
