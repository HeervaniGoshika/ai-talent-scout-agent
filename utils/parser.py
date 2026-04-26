import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def parse_jd(jd_text):

    prompt = f"""
    Extract the following from the job description:
    - skills (list)
    - experience (number in years)
    - role (string)

    Return ONLY valid JSON. No explanation.

    Example:
    {{
        "skills": ["Python", "Machine Learning"],
        "experience": 2,
        "role": "ML Engineer"
    }}

    JD:
    {jd_text}
    """

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0
        }
    )

    result = response.json()
    content = result["choices"][0]["message"]["content"]

    try:
        parsed = json.loads(content)
    except:
        # fallback cleanup
        content = content.replace("```json", "").replace("```", "")
        parsed = json.loads(content)

    return parsed