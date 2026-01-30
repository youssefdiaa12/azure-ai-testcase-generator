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

Return **ONLY** a JSON array (no markdown, no backticks, no explanations).
Each element MUST match this schema:

- title: string
- type: string  # one of: "positive" | "negative" | "edge" (if unsure, use "positive")
- steps: string[]  # array of plain text steps; DO NOT return objects in this array
- expected: string

Acceptance Criteria (Gherkin-like text):
{formatted}

Example of the EXACT shape to return:
[
  {{
    "title": "User can sign in with valid credentials",
    "type": "positive",
    "steps": [
      "Open the login page",
      "Enter a registered email",
      "Enter a valid password",
      "Click Sign in"
    ],
    "expected": "User is redirected to the dashboard"
  }}
]
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    body = { "contents": [{"parts": [{"text": prompt}]}] }

    res = requests.post(url, json=body)
    print("the ai agent response code is "+str(res.status_code))

    # Be defensive: the response can vary; add guards
    j = res.json()
    try:
        text = j["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response shape: {json.dumps(j)[:1000]}") from e

    return extract_json(text)