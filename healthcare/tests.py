from datetime import date
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from healthcare.models import Department, Doctor, DoctorAvailability, Appointment

class HealthcareApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testpatient', password='password123', email='patient@example.com')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.dept = Department.objects.create(name='General Medicine', description='General care')
        self.doctor = Doctor.objects.create(
            name='Alice Smith',
            department=self.dept,
            specialization='General Physician',
            experience_years=10,
            fee=500.00
        )
        self.slot = DoctorAvailability.objects.create(
            doctor=self.doctor,
            date=date.today(),
            start_time='09:00:00',
            end_time='10:00:00',
            is_booked=False
        )

    def test_list_departments(self):
        resp = self.client.get('/api/healthcare/departments/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_list_doctors_and_filter(self):
        resp = self.client.get(f'/api/healthcare/doctors/?department={self.dept.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['name'], 'Alice Smith')

    def test_doctor_availability_listing(self):
        resp = self.client.get(f'/api/healthcare/doctors/{self.doctor.id}/availability/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)

    def test_book_appointment_and_prevent_double_booking(self):
        # 1. Book successfully
        payload = {
            'availability': self.slot.id,
            'patient_name': 'Test Patient',
            'patient_email': 'patient@example.com',
            'reason': 'Checkup'
        }
        resp = self.client.post('/api/healthcare/appointments/', payload, format='json')
        self.assertEqual(resp.status_code, 201)

        # Slot is now marked as booked
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_booked)

        # 2. Attempt double booking should fail
        resp2 = self.client.post('/api/healthcare/appointments/', payload, format='json')
        self.assertEqual(resp2.status_code, 400)

    def test_list_user_appointments(self):
        Appointment.objects.create(
            patient=self.user,
            doctor=self.doctor,
            availability=self.slot,
            patient_name='Test Patient',
            patient_email='patient@example.com',
            reason='Fever'
        )
        resp = self.client.get('/api/healthcare/appointments/list/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
