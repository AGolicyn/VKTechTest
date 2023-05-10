from rest_framework import serializers
from .models import FriendRequest, Friendship, FriendStatus, CustomUser


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["username", "password"]


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ("id", "from_user", "to_user", "created_at")


class FriendshipSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ("id", "user1", "user2", "created_at")


class FriendStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=FriendStatus.CHOICES)
