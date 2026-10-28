import json
import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from .services import generate_ai_response
from healthcare.models import Doctor
from healthcare.serializers import DoctorSerializer

DEPT_ROOT_MAP = {
    'cardio': 'Cardiology',
    'heart': 'Cardiology',
    'derma': 'Dermatology',
    'skin': 'Dermatology',
    'neuro': 'Neurology',
    'brain': 'Neurology',
    'ortho': 'Orthopedics',
    'bone': 'Orthopedics',
    'joint': 'Orthopedics',
    'pedia': 'Pediatrics',
    'child': 'Pediatrics',
    'gynec': 'Gynecology',
    'women': 'Gynecology',
    'general': 'General Medicine',
    'internal': 'General Medicine',
    'physician': 'General Medicine',
}

def clean_parse_json(raw_text):
    """
    Extracts and parses JSON object from raw response safely,
    stripping markdown backticks, explanations, or whitespace.
    """
    if not raw_text:
        return None
        
    text = raw_text.strip()
    
    # 1. Check for markdown code fences: ```json ... ```
    fence_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text, re.IGNORECASE)
    if fence_match:
        try:
            return json.loads(fence_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 2. Direct JSON decode
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # 3. Extract outermost { ... }
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx > start_idx:
        try:
            return json.loads(text[start_idx:end_idx + 1])
        except json.JSONDecodeError:
            pass
            
    return None


class ChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_message = request.data.get('message')
        history = request.data.get('history', [])

        if not user_message:
            return Response({'error': 'Message is required.'}, status=400)

        ai_response = generate_ai_response(user_message, history)
        parsed_reply = clean_parse_json(ai_response)
        
        if not parsed_reply or not isinstance(parsed_reply, dict):
            # Graceful fallback if response wasn't valid JSON
            parsed_reply = {
                "type": "question",
                "message": ai_response.strip() if ai_response else "Could you tell me more about your symptoms?"
            }
            
        # If guidance, resolve matched doctors
        if parsed_reply.get('type') == 'guidance':
            specialties = parsed_reply.get('recommended_specialties', [])
            matched_doctors = []
            seen_doc_ids = set()
            
            for spec in specialties:
                spec_str = str(spec).strip()
                if not spec_str:
                    continue
                    
                # 1. Search directly by department name or specialization
                docs = list(Doctor.objects.filter(
                    Q(department__name__icontains=spec_str) |
                    Q(specialization__icontains=spec_str)
                ).distinct())
                
                # 2. If no direct match, check root map (e.g. 'Cardiologist' -> 'Cardiology')
                if not docs:
                    spec_lower = spec_str.lower()
                    for root, canonical_dept in DEPT_ROOT_MAP.items():
                        if root in spec_lower:
                            docs = list(Doctor.objects.filter(department__name__icontains=canonical_dept).distinct())
                            break
                            
                for doc in docs:
                    if doc.id not in seen_doc_ids:
                        seen_doc_ids.add(doc.id)
                        matched_doctors.append(doc)
                        
            # If no doctors found, provide General Medicine doctors as safe baseline
            if not matched_doctors:
                general_docs = list(Doctor.objects.filter(department__name__icontains="General Medicine"))
                for doc in general_docs:
                    if doc.id not in seen_doc_ids:
                        seen_doc_ids.add(doc.id)
                        matched_doctors.append(doc)

            parsed_reply['matched_doctors'] = DoctorSerializer(matched_doctors, many=True).data

        return Response({
            'reply': parsed_reply
        })
