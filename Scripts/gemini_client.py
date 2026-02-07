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
    text = text.replace(chr(8216), "'").replace(chr(8217), "'")
    text = text.replace(chr(8220), '"').replace(chr(8221), '"')
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
    """Extract JSON array from response."""
    # Try markdown code blocks first
    match = re.search(r"```json\s*(\[[\s\S]*?\])\s*```", text, re.DOTALL)
    if match:
        cleaned = match.group(1).strip()
    else:
        # Try plain array
        match = re.search(r"(\[[\s\S]*\])", text, re.DOTALL)
        if not match:
            raise ValueError("No JSON array found in response")
        cleaned = match.group(1)
    
    # Clean up common issues
    cleaned = cleaned.replace(",]", "]").replace(",}", "}")
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    
    return json.loads(cleaned)

def generate_test_cases(story):
    cleaned = clean_acceptance_criteria(story["acceptance"])
    formatted = format_acceptance_for_prompt(cleaned)
    
    # Detect field types for contextual testing hints
    field_types = []
    if any(x in cleaned.lower() for x in ['email', 'mail']):
        field_types.append("email validation")
    if any(x in cleaned.lower() for x in ['password', 'secret']):
        field_types.append("password requirements")
    if any(x in cleaned.lower() for x in ['date', 'time']):
        field_types.append("date/time validation")
    if any(x in cleaned.lower() for x in ['number', 'price', 'amount']):
        field_types.append("numeric boundaries")
    
    field_hint = f" Also test: {', '.join(field_types)}." if field_types else ""

    prompt = f"""
Generate 8-12 manual test cases for this user story. Include:

**Positive (2-3):** Happy path scenarios
**Negative (3-4):** Validation failures, invalid inputs
**Edge (3-5):** Empty values, boundaries, special chars{field_hint}

Return ONLY this JSON format (no markdown, no explanations):
[
  {{
    "title": "Test case title",
    "type": "positive|negative|edge",
    "steps": ["Step 1", "Step 2"],
    "expected": "Expected result"
  }}
]

Acceptance Criteria:
{formatted}
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    body = { "contents": [{"parts": [{"text": prompt}]}] }

    res = requests.post(url, json=body)
    print(f"AI response code: {res.status_code}")

    j = res.json()
    try:
        text = j["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response: {json.dumps(j)[:500]}") from e

    return extract_json(text)
