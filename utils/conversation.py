import requests
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def simulate_conversation(candidate, parsed_jd):

    # Step 1: Generate recruiter message
    recruiter_prompt = f"""
    You are a recruiter.

    Candidate name: {candidate['name']}
    Candidate skills: {candidate['skills']}
    Job role: {parsed_jd['role']}
    Required skills: {parsed_jd['skills']}

    Write a short personalized outreach message (2 lines max).

    STRICT RULES:
    - Use the candidate name: {candidate['name']}
    - Do NOT invent names like Alexandra or John
    - Do NOT use placeholders like [Candidate Name]
    - Use a consistent recruiter name: Alex
    - Start message with: Hi {candidate['name']}
    - End with: Best regards, Alex
    - Do NOT add brackets like (I am Interested)
    - Keep response natural sentence only
    - Do NOT wrap response in quotes

    Format:
    Hi {candidate['name']},

    ...
    Best regards,
    Alex
    """

    recruiter_response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": recruiter_prompt}],
            "temperature": 0.7
        }
    )

    recruiter_message = recruiter_response.json()["choices"][0]["message"]["content"]

    # Step 2: Candidate response
    candidate_prompt = f"""
    You are a job candidate.

    Candidate skills: {candidate['skills']}
    Experience: {candidate['experience']} years

    Recruiter message:
    "{recruiter_message}"

    Respond in 1–2 lines.

    STRICT RULES:
    - Respond with ONLY ONE final answer
    - Do NOT give alternatives
    - Do NOT include "OR"
    - Do NOT list multiple options
    - Give a single clear response
    - Do NOT wrap response in quotes

    Your response must clearly indicate ONLY ONE:
    
    Interested OR Maybe OR Not interested

    Be strict:
    - If skills do NOT match → lower interest
    - If response is uncertain → Neutral
    - Only mark Interested if clearly strong alignment
    """

    candidate_response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": candidate_prompt}],
            "temperature": 0.7
        }
    )

    candidate_reply = candidate_response.json()["choices"][0]["message"]["content"]

    return {
        "recruiter_message": recruiter_message,
        "candidate_reply": candidate_reply
    }