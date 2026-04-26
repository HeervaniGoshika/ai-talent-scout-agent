import requests
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def extract_json(text):
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group()
    return "{}"


def get_interest_score(response_text):

    prompt = f"""
    STRICT RULES:
    - Return ONLY valid JSON
    - Do NOT include explanation
    - Do NOT include multiple responses

    Be more strict:
    - Strong match → high enthusiasm
    - Partial match → moderate enthusiasm
    - Weak match → low enthusiasm

    Candidate response:
    "{response_text}"

    Classify interest:

    Return:
    {{
        "interest_level": "Interested/Neutral/Not Interested",
        "score": number,
        "reason": "short explanation"
    }}"""

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


    clean_json = extract_json(content)

    try:
        data = json.loads(clean_json)
    except:
        data = {}

    
    if isinstance(data, list):
        data = data[0]

    score = data.get("score", 50)


    if score <= 10:
        score = score * 10

    score = min(max(score, 0), 100)
    score = max(score, 10)

    
    return {
        "interest_level": data.get("interest_level", "Unknown"),
        "score": score,
        "reason": data.get("reason", "Parsing fallback")
    }


def compute_final_scores(candidates):

    final_results = []

    for c in candidates:
        interest_data = get_interest_score(c["response"])

        c["interest_score"] = interest_data["score"]
        c["interest_level"] = interest_data["interest_level"]
        c["interest_reason"] = interest_data["reason"]

        # 🔥 Final weighted score
        c["final_score"] = (
            0.6 * c["match_score"] +
            0.4 * c["interest_score"]
        )

        final_results.append(c)

    return sorted(final_results, key=lambda x: x["final_score"], reverse=True)