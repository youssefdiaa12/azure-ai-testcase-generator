
# 🤖 AI Test Case Generator for Azure DevOps

Automated test case generation using **Gemini AI** with direct integration into **Azure DevOps Test Plans**.

This project reads User Stories from Azure Boards, generates high‑quality manual test cases using AI, and automatically publishes them into Azure DevOps Test Plans using the latest REST APIs.

***

## 🚀 What the System Does

The pipeline automatically:

### ✅ Creates Test Artifacts

| Work Item      | Test Artifact |
| -------------- | ------------- |
| **Epic**       | Test Plan     |
| **Feature**    | Test Suite    |
| **User Story** | Test Cases    |

### ✅ Generates AI‑Powered Test Cases

For every new User Story, the pipeline:

*   Sends acceptance criteria to Gemini AI
*   Generates well‑structured test cases
*   Normalizes and validates AI output
*   Builds proper Azure DevOps test‑step XML
*   Publishes the Test Case work item
*   Links it to the Suite & Story

### ✅ Uses Modern Azure DevOps APIs

*   Creates Test Case work items
*   Adds them to test suites using the **testplan** API
*   Links them back to the parent User Story

### 🧠 Key Enhancements Based on Latest Change

The generator now includes:

#### ✔ AI Output Normalization

Ensures `steps` and `expected` are always clean strings (even if AI outputs lists or objects).

#### ✔ Valid Test Step XML

ADO requires **raw XML tags**, not HTML entities. Now uses:

```xml
<steps>
  <step>
    <parameterizedString>Action</parameterizedString>
    <parameterizedString>Expected</parameterizedString>
  </step>
</steps>
```

#### ✔ New "testplan" API for Suite Linking

Replaces the old-style `/test/Plans/...` endpoint with:

    POST /_apis/testplan/Plans/{planId}/Suites/{suiteId}/TestCase

#### ✔ Strong Error Handling & Logging

*   Per‑case failure logs
*   Response code validation
*   HTTP timeouts
*   Payload debugging on error

***

## 🏗 Architecture Overview

    Epic       → Test Plan
    Feature    → Test Suite
    User Story → Test Cases

The hierarchy is automatically maintained so your tests always follow your work structure.

***

## 🔄 Full Automation Flow

1.  Pipeline runs on a schedule (daily by default)
2.  Fetches **new User Stories** using WIQL
3.  For each story:
    *   Identify parent Feature
    *   Identify parent Epic
    *   Ensure Test Plan & Suite exist
    *   Send acceptance criteria to Gemini
    *   Normalize and validate AI response
    *   Build Azure DevOps Test Case XML
    *   Create Test Case Work Item
    *   Add it to the correct Test Suite
    *   Link it back to the User Story

***

## 🧩 AI Prompt Engineering

Gemini receives structured input:

*   Cleaned acceptance criteria
*   Scenario-separated formatting
*   Strict schema instructions
*   A required JSON array format

The AI is forced to return:

```json
{
  "title": "...",
  "type": "positive | negative | edge",
  "steps": ["..."],
  "expected": "..."
}
```

The generator then validates & normalizes this before generating XML.

***

## 🛠 Tech Stack

*   **Python 3.11**
*   **Azure DevOps REST API (wit + testplan)**
*   **Gemini AI (generateContent API)**
*   **Azure Pipelines (YAML)**
*   **WIQL**
*   **XML step builder for ADO manual test cases**

***

## 📁 Folder Structure (recommended)

    /scripts
       main.py
       test_case_generator.py
       ai_prompt.py
    /readme.md
    /pipeline.yml

***

## 🧪 Output Example in Azure DevOps

Each generated Test Case appears with:

*   Title
*   Assigned To
*   Tags (“AI\_Generated”)
*   Auto‑generated steps
*   Linked parent story
*   Linked test suite and plan

***

## 🎯 Benefits

*   Consistent, high-quality test coverage
*   Zero manual effort for test creation
*   Strong alignment between Dev & QA
*   Standardized test structure across all projects
*   Works fully from Azure Pipelines with no local execution required

***
