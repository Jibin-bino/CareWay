import os
import re
import json
import logging

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

logger = logging.getLogger(__name__)

# Ensure .env is loaded if present
def _ensure_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
        except Exception:
            pass

_ensure_env()


def generate_ai_response(user_message, history=None):
    """
    Generates an AI triage response for healthcare navigation.
    Uses Google Gemini GenAI SDK if GEMINI_API_KEY is available.
    Otherwise, gracefully falls back to clinical symptom-mapping engine.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    
    if not api_key or not genai:
        logger.info("Using smart rule-based healthcare fallback (GEMINI_API_KEY not configured or genai absent).")
        return _fallback_response(user_message, history)
        
    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are CareWay AI, a compassionate healthcare navigation assistant. You MUST NOT diagnose illnesses or prescribe medications. "
            "Your role is to understand user symptoms, assess urgency, guide them to the right medical specialty, and suggest next steps. "
            "You must ALWAYS return your response as a valid JSON object without markdown fences. "
            "If the user's symptoms are vague and need clarification (max 1-2 questions), return: "
            '{"type": "question", "message": "Your helpful question here"} '
            "If the user has provided enough symptom details, or if the situation is urgent, return guidance: "
            '{"type": "guidance", "summary": "Brief summary of symptoms", "general_information": "Educational explanation and advice", "recommended_specialties": ["SpecialtyName"], "urgency": "routine" or "urgent", "disclaimer": "This AI provides general educational navigation only. It does not diagnose or replace professional medical advice."} '
            "IMPORTANT: For 'recommended_specialties', you MUST ONLY CHOOSE from this exact list of hospital departments: "
            "['General Medicine', 'Cardiology', 'Dermatology', 'Neurology', 'Orthopedics', 'Pediatrics', 'Gynecology']. "
            "Output pure JSON only."
        )
        
        contents = []
        if history:
            for msg in history:
                role = "user" if msg.get("role") == "user" else "model"
                raw = msg.get("content", "")
                # Extract clean text if history stored JSON
                try:
                    p = json.loads(raw)
                    if isinstance(p, dict) and "message" in p:
                        raw = p["message"]
                except Exception:
                    pass
                contents.append(
                    types.Content(role=role, parts=[types.Part.from_text(text=str(raw))])
                )
                
        contents.append(
            types.Content(role="user", parts=[types.Part.from_text(text=user_message)])
        )

        models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash']
        last_error = None
        for m in models_to_try:
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.3,
                        response_mime_type="application/json",
                    )
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = e
                logger.warning(f"Gemini model {m} call failed: {e}. Trying next model if available.")
                continue

        logger.error(f"All Gemini models failed: {last_error}. Using fallback engine.")
        return _fallback_response(user_message, history)

    except Exception as e:
        logger.error(f"AI Service Error: {e}")
        return _fallback_response(user_message, history)


def _fallback_response(user_message, history):
    """
    Intelligent healthcare symptom triage engine used when live API is unavailable.
    Accurately classifies urgency, extracts medical departments, and asks targeted questions.
    """
    msg_lower = user_message.lower().strip()
    history_list = history or []
    all_text = (msg_lower + " " + " ".join([str(h.get('content', '')).lower() for h in history_list])).strip()
    
    # 1. Immediate Urgency & Red Flag Detection
    urgent_patterns = [
        "chest pain", "shortness of breath", "cannot breathe", "can't breathe", "difficulty breathing",
        "unconscious", "fainted", "stroke", "slurred speech", "paralysis", "sudden numbness",
        "severe bleeding", "coughing blood", "heart attack", "anaphylaxis", "severe trauma",
        "fracture", "suicid", "worst headache of my life", "crushing pain"
    ]
    is_urgent = any(pattern in all_text for pattern in urgent_patterns)
    
    # 2. Determine specialties
    specialties = []
    
    # Cardiology
    if any(k in all_text for k in ["heart", "chest", "palpitation", "cardio", "high bp", "hypertension", "pulse"]):
        specialties.append("Cardiology")
        
    # Dermatology
    if any(k in all_text for k in ["skin", "rash", "itch", "acne", "hair", "scalp", "eczema", "mole", "allergy", "dermat"]):
        specialties.append("Dermatology")
        
    # Neurology
    if any(k in all_text for k in ["headache", "migraine", "dizziness", "dizzy", "vertigo", "nerve", "brain", "seizure", "tingling", "neuro"]):
        specialties.append("Neurology")
        
    # Orthopedics
    if any(k in all_text for k in ["bone", "joint", "knee", "back pain", "neck pain", "spine", "shoulder", "muscle", "fracture", "sprain", "ortho"]):
        specialties.append("Orthopedics")
        
    # Pediatrics
    if any(k in all_text for k in ["child", "baby", "infant", "toddler", "kid", "pediatric", "daughter", "son"]):
        specialties.append("Pediatrics")
        
    # Gynecology
    if any(k in all_text for k in ["period", "menstrual", "pregnancy", "pregnant", "gynec", "pelvic", "ovary", "uterus", "cramps"]):
        specialties.append("Gynecology")
        
    # General Medicine
    if any(k in all_text for k in ["fever", "cold", "cough", "flu", "sore throat", "stomach", "vomit", "nausea", "diarrhea", "fatigue", "diabetes", "tired"]):
        if not specialties or "General Medicine" not in specialties:
            specialties.append("General Medicine")

    if not specialties:
        specialties = ["General Medicine"]

    # 3. Urgency guidance: if urgent, provide immediate guidance without delaying
    if is_urgent:
        return json.dumps({
            "type": "guidance",
            "summary": "Urgent symptoms requiring immediate medical evaluation detected.",
            "general_information": (
                "You have reported severe or potentially urgent symptoms (such as chest pain or breathing difficulty). "
                "These require immediate medical attention. If you are experiencing sudden severe pain, shortness of breath, "
                "or weakness, please visit an Emergency Department or consult a physician immediately."
            ),
            "recommended_specialties": specialties,
            "urgency": "urgent",
            "disclaimer": "This AI provides educational navigation only and is not a substitute for emergency medical care."
        })

    # 4. Check if we should ask a follow-up question
    # If this is the first turn and the message is very brief (less than 4 words or missing details), ask 1 question
    words = msg_lower.split()
    history_turns = len(history_list)
    
    if history_turns == 0 and len(words) < 5 and not any(k in msg_lower for k in ["day", "week", "month", "hour", "since", "severe", "mild"]):
        if "Cardiology" in specialties:
            q = "I understand you have chest or heart concerns. How long have you felt this, and are you having any shortness of breath or dizziness?"
        elif "Dermatology" in specialties:
            q = "Could you tell me how long the skin issue has been present and whether it is itchy, spreading, or painful?"
        elif "Neurology" in specialties:
            q = "How long have you had this headache or neurological symptom, and does it come with vision changes or nausea?"
        elif "Orthopedics" in specialties:
            q = "Where exactly is the pain located, and did it start after a specific injury, strain, or physical activity?"
        elif "Pediatrics" in specialties:
            q = "How old is the child, and are they running a fever or having trouble eating or drinking fluids?"
        elif "Gynecology" in specialties:
            q = "How long have you noticed these symptoms, and are you experiencing any abdominal or pelvic pain?"
        else:
            q = "Could you describe approximately how many days you have had these symptoms and if you have a fever?"
            
        return json.dumps({
            "type": "question",
            "message": q
        })

    # 5. Provide comprehensive guidance
    spec_text = ", ".join(specialties)
    summary_text = f"You have reported symptoms related to {spec_text.lower()}."
    info_text = (
        f"Based on your description, an evaluation by a specialist in {spec_text} is recommended. "
        "A doctor will be able to perform a proper clinical checkup, review your history, and recommend any necessary tests or treatment."
    )
    
    return json.dumps({
        "type": "guidance",
        "summary": summary_text,
        "general_information": info_text,
        "recommended_specialties": specialties,
        "urgency": "routine",
        "disclaimer": "CareWay AI provides general educational navigation only. It does not diagnose medical conditions or replace clinical evaluation."
    })
