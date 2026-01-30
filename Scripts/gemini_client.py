import requests
import re
import json
import html
import os

API_KEY = os.getenv("GEMINI_API_KEY")

def clean_acceptance_criteria(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    text = re.sub(r'"([^"]+)"', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_acceptance_for_prompt(text: str) -> str:
    scenarios = re.split(r'(?=Scenario:)', text)
    out = ""
    for s in scenarios:
        s = s.strip()
        if s:
            out += f"- {s}\n"
    return out

def extract_json(text):
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
    else:
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON returned by Gemini.")
        cleaned = match.group(1)
    cleaned = cleaned.replace(",]", "]").replace(",}", "}")
    return json.loads(cleaned)

def generate_test_cases(story):

    cleaned = clean_acceptance_criteria(story["acceptance"])
    formatted = format_acceptance_for_prompt(cleaned)

    prompt = f"""
You are a senior QA engineer.
Generate PURE JSON only.
DO NOT write explanations.
DO NOT write markdown.
JSON array only.

Acceptance Criteria:
{formatted}

Your JSON array must contain objects with:
"title", "type", "steps", "expected".
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

    body = { "contents": [{"parts": [{"text": prompt}]}] }

    res = requests.post(url, json=body)
    print("the ai agent response code is "+str(res.status_code))
    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]

    return extract_json(text)