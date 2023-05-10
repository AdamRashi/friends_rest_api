from rest_framework import serializers

from .models import FriendRequest


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = "__all__"


class FriendRequestUpdateSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["accept", "reject"])
    sender_id = serializers.IntegerField()

