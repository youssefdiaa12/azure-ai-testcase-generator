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
    # Use ASCII-friendly quote replacements
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
    """Extract and parse JSON from Gemini response with robust error handling."""
    print(f"DEBUG: Raw AI response length: {len(text)} chars")
    print(f"DEBUG: First 500 chars: {text[:500]}")
    print(f"DEBUG: Last 500 chars: {text[-500:]}")
    
    # Try multiple extraction patterns
    patterns = [
        (r"```json\s*(\[[\s\S]*?\])\s*```", "json-markdown"),
        (r"```\s*(\[[\s\S]*?\])\s*```", "json-backtick"),
        (r"\[\s*\{[\s\S]*?\}[\s\S]*?\]", "json-array"),
        (r"(\[\{[\s\S]*?\}\])", "json-curly"),
    ]
    
    for pattern, pattern_name in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            cleaned = match.group(1).strip()
            print(f"DEBUG: Extracted JSON using {pattern_name}, length: {len(cleaned)}")
            
            # Fix common JSON issues
            cleaned = _fix_json(cleaned)
            
            try:
                return json.loads(cleaned)
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON decode failed with {pattern_name}: {e}")
                continue
    
    # Last resort: try to find any JSON-like structure
    raise ValueError(f"Could not extract valid JSON from response. Response preview: {text[:500]}")


def _fix_json(json_str):
    """Fix common JSON formatting issues."""
    if not json_str:
        return json_str
    
    # Remove trailing commas before } or ]
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    # Fix unquoted keys (basic pattern)
    json_str = re.sub(r'(\w+):', r'"\1":', json_str)
    
    # Remove any markdown or text before/after
    json_str = json_str.strip()
    
    # Try to balance brackets if incomplete
    if json_str.count('[') > json_str.count(']'):
        json_str = json_str + ']' * (json_str.count('[') - json_str.count(']'))
    if json_str.count('{') > json_str.count('}'):
        json_str = json_str + '}' * (json_str.count('{') - json_str.count('}'))
    
    return json_str

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
- title: Descriptive name starting with action
- type: "positive" | "negative" | "edge"
- steps: Sequential, numbered plain text steps
- expected: Clear, specific assertion
- priority: "high" | "medium" | "low" (based on business impact)

### 3. EXAMPLE OUTPUT FORMAT (MUST FOLLOW EXACTLY):
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
  }}
]

### 4. QUANTITY GUIDELINES:
- Positive cases: Minimum 2-3
- Negative cases: Minimum 4-6
- Edge cases: Minimum 5-8
- TOTAL: Aim for 12-20+ test cases depending on story complexity

### 5. TESTING BEST PRACTICES TO FOLLOW:
- Use realistic, meaningful test data
- Include both valid and invalid variations of each input
- Test field interactions
- Consider system state before each test
- Test error messages are user-friendly{field_hint}

## ACCEPTANCE CRITERIA TO TEST:
{formatted}

## OUTPUT REQUIREMENTS:
1. Return ONLY valid JSON array (no markdown, no backticks, no explanations)
2. Each test case MUST have: title, type, priority, steps[], expected
3. Cover all edge case categories mentioned above
4. Use realistic, diverse test data
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
