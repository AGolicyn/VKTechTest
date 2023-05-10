from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from friends.social.models import FriendRequest, Friendship, CustomUser


class SendFriendRequestViewTestCase(APITestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create(username="user1", password="testpas1")
        self.user2 = CustomUser.objects.create(username="user2", password="testpas2")
        self.url = reverse(
            "send_friend_request", kwargs={"username": self.user2.username}
        )
        self.client.force_authenticate(user=self.user1)

    def test_send_friend_request(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FriendRequest.objects.count(), 1)
        self.assertEqual(FriendRequest.objects.first().from_user, self.user1)
        self.assertEqual(FriendRequest.objects.first().to_user, self.user2)

    def test_already_friends(self):
        friendship = Friendship.objects.create(user1=self.user1, user2=self.user2)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Users are already friends."})
        self.assertEqual(FriendRequest.objects.count(), 0)

    def test_request_already_sent(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Friend request already sent."})
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_send_friend_request_with_already_have_request(self):
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        self.client.force_authenticate(user=self.user1)
        url = reverse("send_friend_request", kwargs={"username": self.user2.username})
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Friendship.objects.filter(user1=self.user1, user2=self.user2).exists()
        )
        self.assertFalse(FriendRequest.objects.exists())
