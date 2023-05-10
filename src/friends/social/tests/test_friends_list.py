from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from friends.social.serializers import UserSerializer
from friends.social.models import Friendship, CustomUser


class FriendsViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create(username="user1")
        self.user2 = CustomUser.objects.create(username="user2")
        self.user3 = CustomUser.objects.create(username="user3")
        Friendship.objects.create(user1=self.user1, user2=self.user2)
        Friendship.objects.create(user1=self.user1, user2=self.user3)

    def test_friends_view_with_authenticated_user(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse("friends")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_friends = [self.user2, self.user3]
        serialized_data = UserSerializer(expected_friends, many=True).data
        self.assertEqual(response.data, serialized_data)

    def test_friends_view_with_unauthenticated_user(self):
        self.client.force_authenticate(user=None)
        url = reverse("friends")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
