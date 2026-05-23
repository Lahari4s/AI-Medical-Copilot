from src.llm_client import call_ai

def analyze_food(food_text):
    prompt = f"""
You are a personal nutrition coach.

The user ate:
{food_text}

Analyze clearly:

1. Is this food healthy or unhealthy?
2. Approximate calories
3. Sugar level impact
4. Protein/fiber quality
5. Is it safe for diabetes or weight loss?
6. What should be improved?
7. Better Indian food alternatives
8. Final daily food score out of 10

Give practical advice.
"""
    return call_ai(prompt, max_tokens=1200)