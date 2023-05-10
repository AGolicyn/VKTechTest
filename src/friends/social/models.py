import base64

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class MyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization")
        if not auth:
            return None
        try:
            _, token = auth.split()
            # Декодируем токен и проверяем его на соответствие нашим требованиям
            decoded_token = base64.b64decode(token).decode("utf-8")
            user = CustomUser.objects.get(username=decoded_token.split(":")[0])
            return (user, None)
        except (ValueError, ObjectDoesNotExist):
            raise AuthenticationFailed("Invalid username or password")


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password):
        user = self.model(
            username=username.strip(),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["username", "password"]

    def __str__(self):
        return self.username


class FriendRequest(models.Model):
    from_user = models.ForeignKey(
        CustomUser, related_name="friend_requests_sent", on_delete=models.CASCADE
    )
    to_user = models.ForeignKey(
        CustomUser, related_name="friend_requests_received", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_user", "to_user")


class Friendship(models.Model):
    user1 = models.ForeignKey(
        CustomUser, related_name="friendships1", on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        CustomUser, related_name="friendships2", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user1", "user2")


class FriendStatus:
    NO_REQUEST = "No request"
    INCOMING_REQUEST = "Incoming request"
    OUTGOING_REQUEST = "Outgoing request"
    FRIENDS = "Friends"

    CHOICES = (
        (NO_REQUEST, "No request"),
        (INCOMING_REQUEST, "Incoming request"),
        (OUTGOING_REQUEST, "Outgoing request"),
        (FRIENDS, "Friends"),
    )
