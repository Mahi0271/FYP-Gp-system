from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from audits.models import AuditLog
from records.models import MedicalRecord


class AuditLogAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.gp = User.objects.create_user(username="gp1", password="pass", role=User.Role.GP)
        cls.patient = User.objects.create_user(username="patient1", password="pass", role=User.Role.PATIENT)
        cls.manager = User.objects.create_user(username="manager1", password="pass", role=User.Role.PRACTICE_MANAGER)
        cls.receptionist = User.objects.create_user(username="reception1", password="pass", role=User.Role.RECEPTIONIST)

        cls.record = MedicalRecord.objects.get(patient=cls.patient)

    def setUp(self):
        self.client = APIClient()

    def test_non_manager_cannot_view_audits(self):
        self.client.force_authenticate(self.receptionist)
        resp = self.client.get(reverse("audit_list"))
        self.assertEqual(resp.status_code, 403)

        self.client.force_authenticate(self.gp)
        resp = self.client.get(reverse("audit_list"))
        self.assertEqual(resp.status_code, 403)

        self.client.force_authenticate(self.patient)
        resp = self.client.get(reverse("audit_list"))
        self.assertEqual(resp.status_code, 403)

    def test_manager_can_view_audits(self):
        self.client.force_authenticate(self.manager)
        resp = self.client.get(reverse("audit_list"))
        self.assertEqual(resp.status_code, 200)

    def test_audit_created_on_record_entry_create(self):
        # GP creates an entry -> should write an audit row
        self.client.force_authenticate(self.gp)

        url = reverse("record_entries", args=[self.record.id])
        resp = self.client.post(
            url,
            {"type": "NOTE", "title": "test", "content": "test content"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)

        self.assertTrue(AuditLog.objects.filter(action="RECORD_ENTRY_CREATE").exists())

    def test_audit_filtering_by_action(self):
        # Seed one log
        AuditLog.objects.create(action="TEST_ACTION", object_type="x", metadata={})

        self.client.force_authenticate(self.manager)
        resp = self.client.get(reverse("audit_list") + "?action=TEST_ACTION")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any(item["action"] == "TEST_ACTION" for item in resp.data))
