from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from friends.social.models import CustomUser, FriendRequest


class RejectFriendRequestViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create(username="user1")
        self.user2 = CustomUser.objects.create(username="user2")
        self.friend_request = FriendRequest.objects.create(
            from_user=self.user1, to_user=self.user2
        )

    def test_reject_friend_request_view_with_authenticated_user(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse(
            "reject_friend_request", kwargs={"request_id": self.friend_request.id}
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            FriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

    def test_reject_friend_request_view_with_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        url = reverse("reject_friend_request", args=[self.friend_request.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            FriendRequest.objects.filter(id=self.friend_request.id).exists()
        )

    #
    def test_reject_friend_request_view_with_invalid_request_id(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse("reject_friend_request", kwargs={"request_id": 666})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            FriendRequest.objects.filter(id=self.friend_request.id).exists()
        )
