
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
You mainly need to add **one new section explaining the Regression Test Suite logic**, because your README already explains the AI generation flow well. The new feature is about **test maintenance and regression planning**, not generation.

Below is a **clean section you can append to your README** (in the same style as your document).

---

# 🔁 Automated Regression Test Suite Management

In addition to generating test cases from User Stories, the system now **automatically maintains a Regression Test Suite inside the Test Plan**.

This ensures that **existing functionality potentially affected by new features is always validated during regression cycles.**

---

## 📌 Regression Logic

When a **new User Story** is introduced under a Feature or Epic, it may affect existing functionality already covered by previous test cases.

To ensure system stability, the workflow now supports **linking impacted test cases directly to the new User Story**.

These linked test cases are automatically collected and included in the **Regression Test Suite**.

---

## 🔗 How It Works

### 1️⃣ Link Existing Test Cases to the User Story

Inside **Azure DevOps**, the tester or product owner can link relevant test cases using the **Related** relationship.

Example:

```
Epic
 └── Feature
      └── User Story (New Feature)
           └── Related → Existing Test Case
```

These linked test cases represent **areas that could be impacted by the new change**.

---

### 2️⃣ Pipeline Detects Related Test Cases

During execution, the automation:

1. Reads the **User Story relationships**
2. Detects **linked Test Cases**
3. Collects them as **regression candidates**

---

### 3️⃣ Add Them to the Regression Suite

The system ensures that a **Regression Test Suite exists inside the Test Plan** for the current iteration or release.

Example structure:

```
Test Plan (Epic)
│
├── Feature Test Suite
│   └── AI Generated Test Cases
│
└── Regression Test Suite
    └── Impacted Test Cases
```

If the suite does not exist, it is **created automatically**.

---

### 4️⃣ Automatically Maintain the Regression Suite

The pipeline then:

* Adds all linked test cases to the **Regression Suite**
* Prevents duplicates
* Ensures regression coverage grows as the system evolves

---

## 🔄 Updated Automation Flow

The full pipeline now performs the following:

1. Detect new **User Stories**
2. Generate **AI Test Cases** for the story
3. Create or update:

   * **Test Plan (Epic)**
   * **Feature Test Suite**
4. Detect **Related Test Cases** linked to the story
5. Add those test cases to the **Regression Test Suite**
6. Link all generated and related tests correctly

---

## 🧪 Example Scenario

A new feature is added:

```
Epic: Billing System
Feature: Refund Handling
User Story: Support partial refunds
```

During analysis, the tester identifies existing test cases that could be impacted:

* Refund full payment
* Cancel payment
* Payment status update

These existing test cases are linked to the new User Story.

The pipeline will automatically add them to:

```
Test Plan → Regression Suite
```

ensuring they are executed in the next **iteration or release regression cycle**.

---

## 🎯 Benefits of This Enhancement

✔ Prevents missing regression coverage
✔ Automatically grows regression suite over time
✔ Keeps regression aligned with real system impact
✔ Reduces manual test plan maintenance
✔ Ensures safer feature releases

---

💡 **In short:**

The system now supports **both test generation and intelligent regression suite management**, creating a more complete **AI-assisted QA workflow inside Azure DevOps**.


