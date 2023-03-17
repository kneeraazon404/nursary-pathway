from .models import Notice
from rest_framework.serializers import ModelSerializer


class NoticeSerializer(ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "notice",
            "type",
            "group_user_send",
            "single_user_send",
            "redirect_data",
            "is_visited",
            "is_active",
        ]
