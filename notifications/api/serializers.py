from rest_framework import serializers

from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "seen", "noti", "user_for", "user_from", "about"]
        extra_kwargs = {"seen": {"required": False}}
