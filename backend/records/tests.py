from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from records.models import MedicalRecord, ClinicalEntry


class RecordsAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gp = User.objects.create_user(username="gp1", password="pass", role=User.Role.GP)
        cls.other_gp = User.objects.create_user(username="gp2", password="pass", role=User.Role.GP)

        cls.patient1 = User.objects.create_user(username="patient1", password="pass", role=User.Role.PATIENT)
        cls.patient2 = User.objects.create_user(username="patient2", password="pass", role=User.Role.PATIENT)

        cls.receptionist = User.objects.create_user(
            username="reception1", password="pass", role=User.Role.RECEPTIONIST
        )
        cls.manager = User.objects.create_user(
            username="manager1", password="pass", role=User.Role.PRACTICE_MANAGER
        )

        # Ensure records exist (signals should create them)
        cls.r1 = MedicalRecord.objects.get(patient=cls.patient1)
        cls.r2 = MedicalRecord.objects.get(patient=cls.patient2)

    def setUp(self):
        self.client = APIClient()

    def test_patient_can_view_own_record_me(self):
        self.client.force_authenticate(self.patient1)
        resp = self.client.get(reverse("record_me"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["patient_id"], self.patient1.id)

    def test_patient_cannot_view_other_record(self):
        self.client.force_authenticate(self.patient1)
        resp = self.client.get(reverse("record_detail", args=[self.r2.id]))
        self.assertEqual(resp.status_code, 403)

    def test_patient_cannot_create_entry(self):
        self.client.force_authenticate(self.patient1)
        resp = self.client.post(
            reverse("record_entries", args=[self.r1.id]),
            {"type": "NOTE", "title": "Hi", "content": "test"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_staff_cannot_access_records(self):
        self.client.force_authenticate(self.receptionist)
        resp = self.client.get(reverse("record_detail", args=[self.r1.id]))
        self.assertEqual(resp.status_code, 403)

        self.client.force_authenticate(self.manager)
        resp = self.client.get(reverse("record_detail", args=[self.r1.id]))
        self.assertEqual(resp.status_code, 403)

    def test_assigned_gp_can_read_and_write(self):
        # patient1 was auto-assigned to gp1 (because gp1 created before patient1)
        self.client.force_authenticate(self.gp)

        # Read record
        resp = self.client.get(reverse("record_detail", args=[self.r1.id]))
        self.assertEqual(resp.status_code, 200)

        # Create entry
        resp = self.client.post(
            reverse("record_entries", args=[self.r1.id]),
            {"type": "DIAGNOSIS", "title": "Hypertension", "content": "Stage 1"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["type"], "DIAGNOSIS")

    def test_unassigned_gp_cannot_access(self):
        self.client.force_authenticate(self.other_gp)
        resp = self.client.get(reverse("record_detail", args=[self.r1.id]))
        self.assertEqual(resp.status_code, 403)

        resp = self.client.post(
            reverse("record_entries", args=[self.r1.id]),
            {"type": "NOTE", "title": "x", "content": "y"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)
