def report_analysis_prompt(report_text):
    return f"""
Analyze this medical report.

Return:
1. Summary
2. Abnormal values
3. Possible risks
4. Personalized Indian diet plan
5. Lifestyle plan
6. Exercise
7. Follow-up tests
8. Doctor advice

Report:
{report_text}
"""

def symptom_prompt(symptoms):
    return f"""
Symptoms:
{symptoms}

Provide:
1. Possible causes
2. Urgency level
3. Home care
4. Which doctor to consult
5. Red flag symptoms
6. When to seek emergency care

Do not give final diagnosis.
"""

def prescription_prompt(text):
    return f"""
Analyze this prescription.

Extract:
1. Medicine names
2. Dosage
3. Timing
4. Duration
5. Precautions
6. Side-effect warnings

Prescription:
{text}
"""