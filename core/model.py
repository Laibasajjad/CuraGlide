import os
from groq import Groq

MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b')

def get_client():
    key = os.getenv('GROQ_API_KEY')
    return Groq(api_key=key) if key else None

def analyze_patient(data, language='English'):
    client = get_client()
    if client is None:
        return {'success': False, 'error': 'GROQ_API_KEY is not configured.'}
    prompt = f'''You are CuraGlide, a cautious health-information assistant. You do NOT provide a confirmed diagnosis or replace professional care.

Patient information:
Age: {data.get('age','Not provided')}
Sex/gender: {data.get('gender','Not provided')}
Weight: {data.get('weight','Not provided')} kg
Height: {data.get('height','Not provided')} cm
Conditions: {data.get('conditions','Not provided')}
Medications: {data.get('medications','Not provided')}
Allergies: {data.get('allergies','Not provided')}
History: {data.get('medical_history','Not provided')}
Symptoms: {data.get('symptoms','Not provided')}
Duration: {data.get('duration','Not provided')}

The FIRST line of your reply must be exactly: URGENCY_LEVEL: <LOWER or SOON or URGENT or EMERGENCY>  (this one line is always in English, nothing else on it).
Then respond with these section headings:
WHY THIS URGENCY
WHAT MIGHT BE HAPPENING
WHAT TO DO NOW
WHAT TO MONITOR
WHEN TO GET PROFESSIONAL HELP
IMPORTANT DISCLAIMER
Use calm, clear language. Discuss possibilities, not certainty. Never recommend ignoring serious or worsening symptoms.'''
    if language and language != 'English':
        prompt += (f"\n\nLANGUAGE: Write everything after the URGENCY_LEVEL line in {language}, including the section headings (translate them). "
                   "Use simple natural wording and explain medical terms. The URGENCY_LEVEL line stays in English.")
    try:
        r = client.chat.completions.create(model=MODEL, messages=[{'role':'system','content':'You are a cautious health-information assistant.'},{'role':'user','content':prompt}], temperature=0.3, max_completion_tokens=1600)
        return {'success': True, 'analysis': r.choices[0].message.content}
    except Exception as e:
        return {'success': False, 'error': f'Groq analysis failed: {e}'}
