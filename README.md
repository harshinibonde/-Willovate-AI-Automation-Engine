````markdown
# Willovate AI Automation Engine

An AI-powered business automation engine that converts natural-language instructions into validated browser workflows and executes them on a sample CRM application.

Instead of manually navigating a CRM, users can simply describe what they want:

> Add Priya Mehta as a customer with phone number XXXXXXXXXX

This engine understands the instruction, generates the required workflow, validates it, checks for risk, and executes it through Playwright.

---

## Features

- Natural-language instruction understanding
- Intent detection and entity extraction
- Missing-information detection
- Multi-step workflow planning
- Structured JSON workflow generation
- Workflow validation
- Risk detection and user confirmation
- Browser automation with Playwright
- Error analysis, retry and safe failure handling
- English, Hindi and Hinglish support
- Customer and product management
- Report download
- File upload/download
- Email automation
- Table reading and verification
- Evaluation pipeline

---

## Architecture

```text
                 Natural-Language Instruction
                            |
                            v
                    Intent Detection
                            |
                            v
                    Entity Extraction
                            |
                            v
                 Required Info Check
                            |
                            v
                  Workflow Generation
                            |
                            v
                  Workflow Validation
                            |
                            v
                     Risk Detection
                       /        \
                    Risky       Safe
                      |           |
                      v           |
               User Confirmation |
                      |           |
                      +-----+-----+
                            |
                            v
                   Playwright Runner
                            |
                            v
                      Sample CRM
                            |
                            v
                    Verified Result
````

---

## Workflow

### 1. Intent Detection

The natural-language instruction is converted into a structured intent.

```text
Input:
Add Priya Mehta as a customer with phone number XXXXXXXXXX
```

```json
{
  "intent": "ADD_CUSTOMER",
  "entities": {
    "customer_name": "Priya Mehta",
    "phone_number": "XXXXXXXXXX"
  }
}
```

### 2. Missing Information

Checks whether all information required for the operation is available.

If information is missing, the system asks the user instead of inventing values.

### 3. Workflow Generation

The intent and entities are converted into executable browser actions.

```text
1. OPEN_PAGE | customers
2. CLICK | #add-customer-btn
3. ENTER_TEXT | #customer-name | Pankaj Koche
4. ENTER_TEXT | #phone-number | 9876543210
5. SUBMIT | #save-customer
6. OPEN_PAGE | customers
7. READ_TABLE | #customer-table-body
```

### 4. Workflow Validation

Before execution, the workflow is checked for:

* Valid actions
* Required parameters
* Valid structure
* Executable steps
* Unsupported actions

Invalid actions such as `FAKE_ACTION` are rejected before reaching the automation runner.

### 5. Risk Detection

Destructive actions require confirmation.

```text
Delete Amit from customers
```

```text
Risky workflow: True
Risk type: delete
```

It asks the user for confirmation before executing the action.

### 6. Browser Automation

Validated workflows are executed using Playwright and the result is returned to the user.

---

## Supported Operations

| Category     | Operations            |
| ------------ | --------------------- |
| Customers    | Add, Delete, Read     |
| Products     | Add, Update, Read     |
| Reports      | Download              |
| Files        | Upload, Download      |
| Email        | Send Email            |
| Workflows    | Multi-step execution  |
| Verification | Read tables / results |

---

## Multi-Step Automation

It can combine multiple actions into a single workflow.

Example:

```text
Open the CRM, add Priya Mehta as a customer with phone number
XXXXXXXXXX, save the record and verify that the customer appears
in the table.
```

Generated workflow:

```text
1. OPEN_PAGE | customers
2. CLICK | #add-customer-btn
3. ENTER_TEXT | #customer-name | Pankaj Koche
4. ENTER_TEXT | #phone-number | 9876543210
5. SUBMIT | #save-customer
6. OPEN_PAGE | customers
7. READ_TABLE | #customer-table-body
```

---

## Error Handling

If an automation step fails, engine:

1. Identifies the failed step.
2. Reads the error.
3. Provides a recovery suggestion.
4. Retries the operation.
5. Stops safely if retries fail.

Example:

```text
Automation error:
Locator.wait_for: Timeout

Failed step:
CLICK customer selector

Suggested recovery:
Recheck the page and try an alternative selector.

Automation stopped safely after retry attempts.
```

This prevents browser failures from producing an unhandled application crash.

---

## Language Support

Supports:

* English
* Hindi
* Hinglish

Examples:

```text
Add Priya Mehta as a customer with phone number XXXXXXXXX
```

```text
Priya naam ka customer add karo with phone number XXXXXXXXXX
```

```text
Product ka price 599 kar do
```

---

## Model

The current implementation uses the Groq API with:

```text
openai/gpt-oss-120b
```

The model is used for:

* Intent detection
* Entity extraction
* Natural-language understanding
* Workflow generation
* Structured JSON output

The generated workflow is validated before execution.

---

## Dataset & Evaluation

The evaluation dataset contains:

| Dataset            | Examples |
| ------------------ | -------: |
| Full Dataset       |      400 |
| Development Set    |      320 |
| Evaluation Set     |       80 |
| Reference Examples |       40 |

Reference examples are stored in:

```text
src/willovate/reference_examples.json
```

### Final Evaluation

| Metric                       |      Result |
| ---------------------------- | ----------: |
| Intent Accuracy              | **100.00%** |
| Entity Accuracy              |  **97.50%** |
| Missing-Information Accuracy |  **98.75%** |
| JSON Validity                | **100.00%** |
| Workflow Validation          | **100.00%** |
| Unsupported-Action Rate      |   **0.00%** |
| Hallucination Rate           |   **0.00%** |

### Workflow Results

```text
Workflow attempts:       74
Valid workflows:         74
Generation failures:      0
Validation failures:      0
```

The workflow-generation comparison metric is separate from workflow validity. All 74 evaluated workflows passed workflow validation.

The remaining evaluation errors were mainly related to natural-language date normalization, such as interpreting `Kal` as `yesterday` and normalizing `todays` to `today`.

---

## Technologies

* **Python** — Core implementation
* **GPT-OSS 120B** — Natural-language understanding and workflow generation
* **Groq API** — LLM inference
* **Playwright** — Browser automation
* **Pydantic** — Workflow/schema validation
* **Flask** — Sample CRM backend
* **HTML / CSS / JavaScript** — Sample CRM interface

---

## Project Structure

```text
Willovate AI Automation Engine/
│
├── src/
│   └── willovate/
│       ├── intent_detector.py
│       ├── workflow_generator.py
│       ├── workflow_validator.py
│       ├── automation_runner.py
│       ├── error_handler.py
│       ├── llm_client.py
│       ├── schemas.py
│       └── reference_examples.json
│
├── sample_crm/
│   ├── app.py
│   ├── templates/
│   ├── static/
│   └── uploads/
│
├── run_willovate.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Requirements

* Python 3.10+
* Groq API key
* Internet connection for LLM inference
* Playwright
* Dependencies listed in `requirements.txt`

---

## Installation

```bash
git clone <repository-url>
cd "Willovate AI Automation Engine"

python -m venv venv
```

### Windows

```powershell
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit the `.env` file or expose the API key.

---

## Running the Project

### 1. Start the Sample CRM

```bash
python sample_crm/app.py
```

The CRM runs at:

```text
http://127.0.0.1:5000
```

Keep the CRM running.

### 2. Start

Open another terminal:

```powershell
venv\Scripts\activate
python run_willovate.py
```

Enter a natural-language instruction when prompted:

```text
What should Willovate do?
> Add Pankaj Koche as a customer with phone number 9876543210
```

---

## Final Demonstration

The main end-to-end demonstration is:

```text
Open the CRM, add Pankaj Koche as a customer with phone number
9876543210, save the record and verify that the customer appears
in the table.
```

The complete pipeline is:

```text
Instruction
     ↓
Intent + Entities
     ↓
Missing Information Check
     ↓
Workflow Generation
     ↓
Workflow Validation
     ↓
Risk Check
     ↓
Browser Automation
     ↓
CRM Update
     ↓
Table Verification
     ↓
Final Result
```

---

## Security

The following files must never be committed:

```text
.env
venv/
__pycache__/
*.pyc
*.log
```

These are excluded through `.gitignore`.

---

## Future Scope

* Screenshot and OCR-based UI understanding
* Vision-based UI element detection
* Automatic selector recovery
* Improved bulk-operation handling
* Better multilingual normalization
* Support for additional web applications
* Advanced workflow recovery
* Standalone web interface
* API deployment

---

## Objective

It demonstrates how an AI system can convert high-level natural-language business instructions into safe, validated and executable browser automation workflows.

```text
Natural Language
       ↓
AI Understanding
       ↓
Intent + Entities
       ↓
Workflow Generation
       ↓
Validation
       ↓
Risk Detection
       ↓
Browser Automation
       ↓
Error Recovery
       ↓
Verified Result
```

The project provides a foundation for intelligent automation across CRM systems and other web-based business applications.

```
```
