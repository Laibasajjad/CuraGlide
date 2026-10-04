import os,json
from groq import Groq
from core.languages import lang_instruction
MODEL=os.getenv('GROQ_MODEL','openai/gpt-oss-20b')

def _client():
    key=os.getenv('GROQ_API_KEY'); return Groq(api_key=key) if key else None

def generate_case(topic,difficulty,case_type,custom_request='',language='English'):
    c=_client()
    if not c:return {'error':'GROQ_API_KEY is not configured.'}
    prompt=f'''Create one fictional educational clinical reasoning case. Topic: {topic}. Difficulty: {difficulty}. Type: {case_type}. Custom request: {custom_request or 'None'}.
Return ONLY valid JSON with title, professor_intro, patient (age, description, opening_presentation), initial_information (array), investigation_areas (exactly 8 objects with question, answer, teaching_point), possible_explanations (array), warning_signs (array), professor_hints (array), final_review (object with key_lesson). Do not reveal a confirmed diagnosis in the opening.'''
    prompt+=lang_instruction(language)
    try:
        r=c.chat.completions.create(model=MODEL,messages=[{'role':'system','content':'Return valid JSON only. Cases are fictional and educational.'},{'role':'user','content':prompt}],response_format={'type':'json_object'},temperature=.7,max_completion_tokens=5000)
        return {'success':True,'case':json.loads(r.choices[0].message.content)}
    except Exception as e:return {'error':f'Case generation failed: {e}'}

def answer_student_question(case,question,conversation,language='English'):
    c=_client()
    if not c:return {'error':'GROQ_API_KEY is not configured.'}
    prompt=f'''You are a professor running a fictional educational clinical reasoning case. Case JSON: {json.dumps(case)}. Previous conversation: {json.dumps(conversation[-10:])}. Student asks: {question}. Answer only what the question reasonably reveals; do not reveal the final answer too early. Return JSON with answer, teaching_point, professor_hint.'''
    prompt+=lang_instruction(language)
    try:
        r=c.chat.completions.create(model=MODEL,messages=[{'role':'system','content':'Return valid JSON only.'},{'role':'user','content':prompt}],response_format={'type':'json_object'},temperature=.4,max_completion_tokens=1200)
        return json.loads(r.choices[0].message.content)
    except Exception as e:return {'error':f'Professor response failed: {e}'}

def review_reasoning(case,reasoning,conversation,language='English'):
    c=_client()
    if not c:return {'error':'GROQ_API_KEY is not configured.'}
    prompt=f'''Review a student's reasoning for this fictional educational case. Case: {json.dumps(case)}. Conversation: {json.dumps(conversation[-12:])}. Reasoning: {reasoning}. Return JSON with overall_feedback, what_went_well (array), what_was_missed (array), important_warning_signs (array), key_lesson. Do not present this as real medical care.'''
    prompt+=lang_instruction(language)
    try:
        r=c.chat.completions.create(model=MODEL,messages=[{'role':'system','content':'Return valid JSON only.'},{'role':'user','content':prompt}],response_format={'type':'json_object'},temperature=.4,max_completion_tokens=1500)
        return {'success':True,'review':json.loads(r.choices[0].message.content)}
    except Exception as e:return {'error':f'Professor review error: {e}'}
