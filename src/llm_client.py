from openai import OpenAI
from src.config import OPENROUTER_API_KEY, BASE_URL

client = OpenAI(
    base_url=BASE_URL,
    api_key=OPENROUTER_API_KEY
)

def call_ai(prompt, max_tokens=1200):
    models = [
        "openrouter/auto",
        "deepseek/deepseek-chat",
        "google/gemma-3-12b-it"
    ]

    last_error = ""

    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )

            answer = response.choices[0].message.content

            if answer and answer.strip():
                return answer

        except Exception as e:
            last_error = str(e)

    return f"AI service error: {last_error}"