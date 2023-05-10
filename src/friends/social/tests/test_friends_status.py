from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from friends.social.models import FriendRequest, Friendship, CustomUser, FriendStatus


class FriendStatusViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create(username="user1")
        self.user2 = CustomUser.objects.create(username="user2")
        self.user3 = CustomUser.objects.create(username="user3")
        Friendship.objects.create(user1=self.user1, user2=self.user2)
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user3)

    def test_friend_status_view_with_friends(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("friend_status", kwargs={"username": self.user2.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"status": FriendStatus.FRIENDS}
        self.assertEqual(response.data, expected_data)

    def test_friend_status_view_with_outgoing_request(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse("friend_status", kwargs={"username": self.user3.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"status": FriendStatus.OUTGOING_REQUEST}
        self.assertEqual(response.data, expected_data)

    def test_friend_status_view_with_incoming_request(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse("friend_status", kwargs={"username": self.user2.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"status": FriendStatus.INCOMING_REQUEST}
        self.assertEqual(response.data, expected_data)

    def test_friend_status_view_with_no_request(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("friend_status", kwargs={"username": self.user3.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {"status": FriendStatus.NO_REQUEST}
        self.assertEqual(response.data, expected_data)

    def test_friend_status_view_with_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        url = reverse("friend_status", args=[self.user2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
