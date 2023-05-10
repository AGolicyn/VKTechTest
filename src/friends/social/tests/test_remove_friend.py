from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from friends.social.serializers import UserSerializer
from friends.social.models import FriendRequest, Friendship, CustomUser, FriendStatus


class RemoveFriendViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create(username="user1")
        self.user2 = CustomUser.objects.create(username="user2")
        Friendship.objects.create(user1=self.user1, user2=self.user2)

    def test_remove_friend_view_with_authenticated_user(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("remove_friend", kwargs={"username": self.user2.username})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Friendship.objects.filter(user1=self.user1, user2=self.user2).exists()
        )

    def test_remove_friend_view_with_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        url = reverse("remove_friend", kwargs={"username": self.user2.username})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            Friendship.objects.filter(user1=self.user1, user2=self.user2).exists()
        )

    def test_remove_friend_view_with_nonexistent_user(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("remove_friend", kwargs={"username": "dummy"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Friendship.objects.filter(user1=self.user1, user2=self.user2).exists()
        )

    def test_remove_friend_view_with_non_friend_user(self):
        self.client.force_authenticate(user=self.user1)
        user3 = CustomUser.objects.create(username="user3")
        url = reverse("remove_friend", kwargs={"username": user3.username})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Friendship.objects.filter(user1=self.user1, user2=self.user2).exists()
        )
