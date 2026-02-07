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
    
    # Extract potential field types from acceptance criteria for contextual hints
    field_types = []
    if any(x in cleaned.lower() for x in ['email', 'mail']):
        field_types.append("email (valid format, invalid format, missing @, special chars)")
    if any(x in cleaned.lower() for x in ['password', 'secret', 'pin']):
        field_types.append("password/security fields (length limits, special chars, encoding)")
    if any(x in cleaned.lower() for x in ['date', 'time', 'deadline']):
        field_types.append("date/time (future, past, current, timezone, format)")
    if any(x in cleaned.lower() for x in ['number', 'amount', 'quantity', 'price']):
        field_types.append("numeric fields (zero, negative, decimals, boundaries)")
    if any(x in cleaned.lower() for x in ['file', 'upload', 'image', 'document']):
        field_types.append("file uploads (type, size, empty, corrupted)")
    if any(x in cleaned.lower() for x in ['search', 'filter', 'find']):
        field_types.append("search/filter (wildcards, special chars, empty, long text)")
    if any(x in cleaned.lower() for x in ['phone', 'mobile', 'tel']):
        field_types.append("phone numbers (format, country code, special chars)")
    if any(x in cleaned.lower() for x in ['address', 'location', 'city', 'country']):
        field_types.append("address fields (special chars, unicode, length)")
    
    field_hint = f"\nRelevant field types to test: {', '.join(field_types)}" if field_types else ""

    prompt = f"""
You are a senior QA engineer with 15+ years of experience in comprehensive test design.

Your task is to generate thorough, high-quality test cases from the given acceptance criteria.

## CRITICAL REQUIREMENTS:

### 1. EDGE CASE CATEGORIES (MANDATORY COVERAGE):
For each user story, you MUST generate test cases from these categories:

**Positive Cases (Happy Path):**
- Standard workflow with valid data
- Best case scenarios that satisfy acceptance criteria

**Negative Cases (Validation & Error Handling):**
- Missing required fields
- Invalid data formats (wrong type, malformed input)
- Boundary violations (exceeds max, below min)
- Special characters and unicode
- SQL injection, XSS attempts
- Duplicate entries
- Unauthorized access attempts

**Edge Cases (Boundary & Corner Conditions):**
- Empty strings, null, undefined values
- Whitespace only inputs
- Maximum and minimum length boundaries
- Leading/trailing spaces
- Numeric boundaries (0, -1, max int, overflow)
- Date boundaries (leap year, timezones, daylight saving)
- Empty collections/lists
- Single item in collections
- Large datasets (performance edge)
- Concurrent access/modification
- Session timeout scenarios
- Network interruption points

**UI/UX Edge Cases:**
- Double-clicking submit buttons
- Rapid form submissions
- Browser back/forward navigation
- Page refresh during operations
- Multiple browser tabs

### 2. COMPREHENSIVE TEST CASE STRUCTURE:
Each test case MUST include:
- title: Descriptive name starting with action (e.g., "Verify user can...", "Validate that...", "Ensure... fails when...")
- type: "positive" | "negative" | "edge"
- steps: Sequential, numbered plain text steps
- expected: Clear, specific assertion
- priority: "high" | "medium" | "low" (based on business impact)

### 3. EXAMPLE OUTPUT FORMAT (MUST FOLLOW EXACTLY):
```json
[
  {{
    "title": "User successfully logs in with valid credentials",
    "type": "positive",
    "priority": "high",
    "steps": [
      "Navigate to login page",
      "Enter registered email 'user@example.com'",
      "Enter valid password 'SecurePass123'",
      "Click Sign In button"
    ],
    "expected": "User is redirected to dashboard, welcome message displays"
  }},
  {{
    "title": "Login fails with invalid email format",
    "type": "negative",
    "priority": "high",
    "steps": [
      "Navigate to login page",
      "Enter invalid email 'invalid-email'",
      "Enter any password",
      "Click Sign In button"
    ],
    "expected": "Error message 'Please enter a valid email address' displays"
  }},
  {{
    "title": "Login fails with empty email field",
    "type": "edge",
    "priority": "high",
    "steps": [
      "Navigate to login page",
      "Leave email field empty",
      "Enter valid password",
      "Click Sign In button"
    ],
    "expected": "Error message 'Email is required' displays below field"
  }},
  {{
    "title": "Login fails when password exceeds maximum length",
    "type": "edge",
    "priority": "medium",
    "steps": [
      "Navigate to login page",
      "Enter valid email",
      "Enter password longer than 128 characters",
      "Click Sign In button"
    ],
    "expected": "Form validation prevents submission, error message about max length"
  }},
  {{
    "title": "SQL injection attempt in email field",
    "type": "security",
    "priority": "high",
    "steps": [
      "Navigate to login page",
      "Enter email: \"' OR '1'='1\"--\"",
      "Enter any password",
      "Click Sign In button"
    ],
    "expected": "Input sanitized, error message displays, no database access"
  }},
  {{
    "title": "User cannot login with correct credentials after session timeout",
    "type": "edge",
    "priority": "medium",
    "steps": [
      "Login with valid credentials",
      "Wait for session timeout (30 minutes)",
      "Attempt to access protected page",
      "Observe system response"
    ],
    "expected": "User redirected to login page, appropriate timeout message displays"
  }}
]
```

### 4. QUANTITY GUIDELINES:
- Positive cases: Minimum 2-3
- Negative cases: Minimum 4-6 (covering major validation rules)
- Edge cases: Minimum 5-8 (covering boundaries, nulls, special chars)
- TOTAL: Aim for 12-20+ test cases depending on story complexity

### 5. TESTING BEST PRACTICES TO FOLLOW:
- Use realistic, meaningful test data (not 'test123' for everything)
- Include both valid and invalid variations of each input
- Test field interactions (how fields affect each other)
- Consider system state before each test
- Include cleanup steps if tests modify persistent data
- Test error messages are user-friendly and actionable
- Consider accessibility (keyboard navigation, screen readers){field_hint}

## ACCEPTANCE CRITERIA TO TEST:
{formatted}

## OUTPUT REQUIREMENTS:
1. Return ONLY valid JSON array (no markdown, no backticks, no explanations)
2. Each test case MUST have: title, type, priority, steps[], expected
3. Cover all edge case categories mentioned above
4. Use realistic, diverse test data
5. Ensure steps are numbered and sequential
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