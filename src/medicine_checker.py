def check_medicine_safety(text):
    text = text.lower()
    warnings = []

    if "metformin" in text:
        warnings.append("ℹ Metformin is commonly used for diabetes. Take only as prescribed.")

    if "thyroxine" in text or "eltroxin" in text:
        warnings.append("ℹ Thyroid medicine is usually taken on empty stomach.")

    if "bp" in text or "blood pressure" in text:
        warnings.append("⚠ Monitor salt intake and BP regularly.")

    if len(warnings) == 0:
        warnings.append("✅ No obvious medicine warning detected.")

    return warnings