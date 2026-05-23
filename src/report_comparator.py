from src.llm_client import call_ai

def compare_reports(old_report, new_report):
    prompt = f"""
Compare these two medical reports.

OLD REPORT:
{old_report}

NEW REPORT:
{new_report}

Explain:
1. Improvements
2. Worsening values
3. Risk changes
4. Lifestyle recommendations
5. Doctor follow-up needed
"""
    return call_ai(prompt, max_tokens=1500)