from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from friends.social.models import FriendRequest, CustomUser
from friends.social.serializers import FriendRequestSerializer


class FriendRequestsViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            username="user1", password="testpas1"
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2", password="testpas2"
        )
        self.friend_request1 = FriendRequest.objects.create(
            from_user=self.user1, to_user=self.user2
        )
        self.friend_request2 = FriendRequest.objects.create(
            from_user=self.user2, to_user=self.user1
        )

    def test_friend_requests_view(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("friend_requests")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["sent"]), 1)
        self.assertEqual(len(response.data["received"]), 1)
        serializer_sent = FriendRequestSerializer(self.friend_request1)
        serializer_received = FriendRequestSerializer(self.friend_request2)
        self.assertEqual(response.data["sent"][0], serializer_sent.data)
        self.assertEqual(response.data["received"][0], serializer_received.data)
