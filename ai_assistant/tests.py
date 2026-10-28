import json
from django.test import TestCase
from rest_framework.test import APIClient
from healthcare.models import Department, Doctor
from ai_assistant.services import generate_ai_response
from ai_assistant.views import clean_parse_json

class AIAssistantTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.dept_cardio = Department.objects.create(name="Cardiology", description="Heart health")
        self.dept_derma = Department.objects.create(name="Dermatology", description="Skin health")
        self.doctor_cardio = Doctor.objects.create(
            name="Carol Williams",
            department=self.dept_cardio,
            specialization="Cardiologist",
            experience_years=12,
            fee=1000.00
        )
        self.doctor_derma = Doctor.objects.create(
            name="Eve Davis",
            department=self.dept_derma,
            specialization="Dermatologist",
            experience_years=5,
            fee=750.00
        )

    def test_json_clean_parser(self):
        # Plain json
        res1 = clean_parse_json('{"type": "question", "message": "How long?"}')
        self.assertEqual(res1.get("type"), "question")

        # Markdown wrapped
        res2 = clean_parse_json('```json\n{"type": "guidance", "urgency": "urgent"}\n```')
        self.assertEqual(res2.get("urgency"), "urgent")

        # Leading/trailing text
        res3 = clean_parse_json('Here is your response: {"type": "guidance", "urgency": "routine"} Thank you.')
        self.assertEqual(res3.get("urgency"), "routine")

    def test_ai_response_urgent_symptoms(self):
        response_str = generate_ai_response("I have severe crushing chest pain and shortness of breath")
        data = clean_parse_json(response_str)
        self.assertEqual(data.get("type"), "guidance")
        self.assertEqual(data.get("urgency"), "urgent")
        self.assertIn("Cardiology", data.get("recommended_specialties", []))

    def test_ai_response_initial_brief_question(self):
        response_str = generate_ai_response("headache")
        data = clean_parse_json(response_str)
        self.assertEqual(data.get("type"), "question")
        self.assertIn("message", data)

    def test_chat_api_endpoint_guidance_and_doctor_matching(self):
        resp = self.client.post('/api/ai/chat/', {
            'message': 'I have had an itchy skin rash for 2 weeks',
            'history': []
        }, format='json')

        self.assertEqual(resp.status_code, 200)
        reply = resp.data.get('reply', {})
        self.assertEqual(reply.get('type'), 'guidance')
        matched = reply.get('matched_doctors', [])
        self.assertGreater(len(matched), 0)
        self.assertEqual(matched[0]['name'], 'Eve Davis')

    def test_chat_api_requires_message(self):
        resp = self.client.post('/api/ai/chat/', {}, format='json')
        self.assertEqual(resp.status_code, 400)
