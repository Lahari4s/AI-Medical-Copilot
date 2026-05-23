def predict_possible_conditions(report_text):
    text = report_text.lower()
    conditions = []

    if "glucose" in text or "diabetes" in text:
        conditions.append("⚠ Diabetes / prediabetes risk should be evaluated")

    if "cholesterol" in text:
        conditions.append("⚠ Cardiovascular risk may be present")

    if "thyroid" in text or "tsh" in text:
        conditions.append("⚠ Thyroid imbalance may need review")

    if "bp" in text or "blood pressure" in text:
        conditions.append("⚠ Hypertension risk may be present")

    if len(conditions) == 0:
        conditions.append("✅ No major rule-based disease risk detected")

    return conditions