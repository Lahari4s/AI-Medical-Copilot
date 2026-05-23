import re

def detect_abnormal_values(report_text):
    text = report_text.lower()
    findings = []

    glucose_values = re.findall(r"glucose.*?(\d+)", text)

    for value in glucose_values:
        value = int(value)

        if value >= 126:
            findings.append({
                "test": "Glucose",
                "value": value,
                "severity": "High",
                "message": "Possible diabetes range"
            })
        elif value >= 100:
            findings.append({
                "test": "Glucose",
                "value": value,
                "severity": "Moderate",
                "message": "Prediabetes risk"
            })

    cholesterol_values = re.findall(r"cholesterol.*?(\d+)", text)

    for value in cholesterol_values:
        value = int(value)

        if value >= 240:
            findings.append({
                "test": "Cholesterol",
                "value": value,
                "severity": "High",
                "message": "High cholesterol risk"
            })
        elif value >= 200:
            findings.append({
                "test": "Cholesterol",
                "value": value,
                "severity": "Moderate",
                "message": "Borderline cholesterol"
            })

    return findings