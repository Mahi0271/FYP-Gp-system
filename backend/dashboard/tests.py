from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User

class DashboardAPITests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username="mgr_dash", password="pass", role=User.Role.PRACTICE_MANAGER)
        self.patient = User.objects.create_user(username="pt_dash", password="pass", role=User.Role.PATIENT)

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    def test_manager_can_view_dashboard(self):
        self._auth(self.manager)
        url = reverse("dashboard")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("appointments", resp.data)
        self.assertIn("records", resp.data)
        self.assertIn("entries", resp.data)
        self.assertIn("audits", resp.data)

    def test_non_manager_denied(self):
        self._auth(self.patient)
        url = reverse("dashboard")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_dates(self):
        self._auth(self.manager)
        url = reverse("dashboard")
        resp = self.client.get(url, {"date_from": "bad-date"})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)