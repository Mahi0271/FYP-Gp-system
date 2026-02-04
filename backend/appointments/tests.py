from datetime import datetime, timedelta

from django.urls import reverse
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from appointments.models import Appointment


class AppointmentAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a GP first so patient signal can auto-assign
        cls.gp = User.objects.create_user(username="gp1", password="pass", role=User.Role.GP)

        cls.receptionist = User.objects.create_user(
            username="reception1", password="pass", role=User.Role.RECEPTIONIST
        )

        cls.patient1 = User.objects.create_user(
            username="patient1", password="pass", role=User.Role.PATIENT
        )
        cls.patient2 = User.objects.create_user(
            username="patient2", password="pass", role=User.Role.PATIENT
        )

        tz = timezone.get_current_timezone()
        tomorrow = timezone.now().date() + timedelta(days=1)

        def dt(h, m):
            return timezone.make_aware(datetime.combine(tomorrow, datetime.min.time()).replace(hour=h, minute=m), tz)

        cls.a1 = Appointment.objects.create(
            patient=cls.patient1,
            gp=cls.gp,
            start_time=dt(10, 0),
            end_time=dt(10, 30),
            status=Appointment.Status.CONFIRMED,
            reason="checkup",
        )
        cls.a2 = Appointment.objects.create(
            patient=cls.patient2,
            gp=cls.gp,
            start_time=dt(11, 0),
            end_time=dt(11, 30),
            status=Appointment.Status.CONFIRMED,
            reason="follow up",
        )

    def setUp(self):
        self.client = APIClient()

    def test_patient_can_cancel_only(self):
        self.client.force_authenticate(self.patient1)
        url = reverse("appointment_detail", args=[self.a1.id])
        resp = self.client.patch(url, {"status": Appointment.Status.CANCELLED}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.a1.refresh_from_db()
        self.assertEqual(self.a1.status, Appointment.Status.CANCELLED)

    def test_patient_cannot_reschedule(self):
        self.client.force_authenticate(self.patient1)
        url = reverse("appointment_detail", args=[self.a1.id])

        new_start = self.a1.start_time + timedelta(hours=1)
        new_end = self.a1.end_time + timedelta(hours=1)

        resp = self.client.patch(
            url,
            {"start_time": new_start.isoformat(), "end_time": new_end.isoformat()},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("detail", resp.data)

    def test_gp_can_complete_only(self):
        self.client.force_authenticate(self.gp)
        url = reverse("appointment_detail", args=[self.a2.id])
        resp = self.client.patch(url, {"status": Appointment.Status.COMPLETED}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.a2.refresh_from_db()
        self.assertEqual(self.a2.status, Appointment.Status.COMPLETED)

    def test_gp_cannot_reschedule(self):
        self.client.force_authenticate(self.gp)
        url = reverse("appointment_detail", args=[self.a2.id])

        new_start = self.a2.start_time + timedelta(hours=1)
        new_end = self.a2.end_time + timedelta(hours=1)

        resp = self.client.patch(
            url,
            {"start_time": new_start.isoformat(), "end_time": new_end.isoformat()},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("detail", resp.data)

    def test_staff_can_reschedule(self):
        self.client.force_authenticate(self.receptionist)
        url = reverse("appointment_detail", args=[self.a1.id])

        new_start = self.a1.start_time + timedelta(hours=2)
        new_end = self.a1.end_time + timedelta(hours=2)

        resp = self.client.patch(
            url,
            {"start_time": new_start.isoformat(), "end_time": new_end.isoformat()},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        self.a1.refresh_from_db()
        self.assertEqual(self.a1.start_time, new_start)
        self.assertEqual(self.a1.end_time, new_end)

    def test_staff_reschedule_overlap_is_blocked(self):
        self.client.force_authenticate(self.receptionist)
        url = reverse("appointment_detail", args=[self.a1.id])

        # Move a1 to overlap a2 (11:00-11:30)
        resp = self.client.patch(
            url,
            {"start_time": self.a2.start_time.isoformat(), "end_time": self.a2.end_time.isoformat()},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("gp", resp.data)

    def test_receptionist_upcoming_filter(self):
        # Create a past appointment
        past_start = timezone.now() - timedelta(days=1)
        past_end = past_start + timedelta(minutes=30)
        Appointment.objects.create(
            patient=self.patient1,
            gp=self.gp,
            start_time=past_start,
            end_time=past_end,
            status=Appointment.Status.CONFIRMED,
        )

        self.client.force_authenticate(self.receptionist)
        url = reverse("appointment_list_create")
        resp = self.client.get(url + "?upcoming=1")
        self.assertEqual(resp.status_code, 200)

        # should not include the past appointment
        now = timezone.now()
        for item in resp.data:
            dt = datetime.fromisoformat(item["start_time"].replace("Z", "+00:00"))
            self.assertGreaterEqual(dt, now)

    def test_patient_cannot_view_others_appointment(self):
        self.client.force_authenticate(self.patient1)
        url = reverse("appointment_detail", args=[self.a2.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)

