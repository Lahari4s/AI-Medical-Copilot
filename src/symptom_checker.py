from src.llm_client import call_ai

def check_symptoms(symptoms):
    prompt = f"""
You are an AI symptom checker.

User symptoms:
{symptoms}

Give:

1. Possible common causes
2. Urgency level: Low / Moderate / Emergency
3. Home care advice
4. Which doctor to consult
5. Red flag symptoms
6. When to seek emergency help

Do not give final diagnosis.
"""
    return call_ai(prompt, max_tokens=1200)