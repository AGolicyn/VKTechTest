from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class RegistrationViewTestCase(APITestCase):
    def test_valid_registration(self):
        url = reverse("registration")
        data = {"username": "testuser", "password": "testpas"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_registration(self):
        url = reverse("registration")
        data = {"username": ""}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)
