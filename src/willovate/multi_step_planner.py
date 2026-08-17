import json
import re

from willovate.llm_client import LLMClient
from willovate.schemas import Workflow


class MultiStepPlanner:

    def __init__(self):
        self.llm = LLMClient()

    def plan(self, instruction: str) -> Workflow:

        system_prompt = """
You are a browser automation workflow planner.

Break a compound user instruction into an ordered sequence of browser actions.

Supported actions:
OPEN_URL
OPEN_PAGE
CLICK
ENTER_TEXT
SELECT_OPTION
UPLOAD_FILE
DOWNLOAD_FILE
READ_TEXT
READ_TABLE
SCROLL
WAIT
SUBMIT
TAKE_SCREENSHOT

For the sample CRM:
- Customer name input: #customer-name
- Phone input: #phone-number
- Save button: #save-customer
- Customer table: #customer-table-body
- Customer form: #customer-form

Rules:
- For the sample CRM, ALWAYS use OPEN_PAGE with target "crm".
- NEVER use OPEN_URL for the sample CRM.
- NEVER CLICK the customer form.
- NEVER CLICK the customer table.
- To enter customer information, directly use ENTER_TEXT.
- To save a customer, use SUBMIT with target "#save-customer".
- To verify a customer was added, use READ_TABLE with target "#customer-table-body".
- Do not add WAIT unless explicitly requested.
- Do not use READ_TEXT for customer verification.
- Do not add actions that are not necessary to complete the instruction.
- Preserve the user's requested order.
- Use ONLY supported actions.
- Never invent user data.
- Return ONLY valid JSON.

Return exactly:

{
    "steps": [
        {
            "action": "ACTION",
            "target": "TARGET",
            "value": "VALUE"
        }
    ]
}
"""

        raw_response = self.llm.chat(
            system_prompt=system_prompt,
            user_message=instruction,
        )

        # Remove markdown code fences if the model adds them
        cleaned = raw_response.strip()
        cleaned = re.sub(r"```json\s*", "", cleaned)
        cleaned = re.sub(r"```\s*", "", cleaned)

        # Extract the JSON object if the model adds explanatory text
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "LLM did not return a valid JSON workflow."
            )

        json_text = cleaned[start:end + 1]

        # Validate that it is valid JSON first
        json.loads(json_text)

        # Then validate against our Pydantic Workflow schema
        return Workflow.model_validate_json(json_text)