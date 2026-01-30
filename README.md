# 🤖 AI Test Case Generator for Azure DevOps

This project automates test case generation using **Gemini AI** and integrates directly with **Azure DevOps Test Management**.

The pipeline scans newly created User Stories and automatically:

- Creates Test Plans from Epics
- Creates Test Suites from Features
- Generates Positive & Negative Test Cases using AI
- Assigns Test Cases automatically

---

##  Architecture Overview

User Story → Feature → Epic hierarchy is used to build test structure:

| Work Item | Test Artifact |
|-----------|------------|
| Epic | Test Plan |
| Feature | Test Suite |
| User Story | Test Cases |

---

##  How It Works

1. Pipeline runs every day
2. Queries Azure DevOps for newly created User Stories
3. For each User Story:
   - Finds parent Feature
   - Finds parent Epic
4. Checks if Test Plan exists for Epic
5. Checks if Test Suite exists for Feature
6. Sends User Story to Gemini AI
7. Creates Test Cases in Azure DevOps
8. Assigns test cases automatically

---

##  AI Prompt Engineering

Gemini AI is used to generate:

- Positive test cases
- Negative test cases
- Structured outputs for Azure Test Management

---

##  Tech Stack

- Python
- Azure DevOps REST API
- Gemini AI API
- Azure Pipelines
- WIQL Queries


