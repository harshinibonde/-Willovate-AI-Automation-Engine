import json
import re
from pathlib import Path

from willovate.llm_client import LLMClient
from willovate.schemas import IntentDetectionResponse


class IntentDetector:
    def __init__(self):
        self.llm = LLMClient()
        self.reference_examples = self._load_reference_examples()

    @staticmethod
    def _load_reference_examples():
        path = Path(__file__).resolve().parent / "reference_examples.json"

        if not path.exists():
            return []

        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)

            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _build_reference_prompt(self):
        if not self.reference_examples:
            return ""

        lines = [
            "\nREFERENCE EXAMPLES:",
            "Use these examples as guidance for intent and entity extraction.",
            "Do not copy entity values from the examples.",
            "Extract values only from the current user instruction.",
            ""
        ]

        for example in self.reference_examples:
            lines.append(f"User: {example.get('instruction', '')}")
            lines.append(
                f"Intent: {example.get('intent', '')}"
            )
            lines.append(
                f"Entities: {json.dumps(example.get('entities', {}), ensure_ascii=False)}"
            )
            lines.append("")

        return "\n".join(lines)

    def detect(self, user_instruction: str) -> IntentDetectionResponse:
        system_prompt = """
You are the intent detection component of an AI automation engine.

Your task is to identify the user's intent and extract relevant entities.

Supported intents:
- ADD_CUSTOMER
- ADD_PRODUCT
- UPDATE_PRODUCT
- DOWNLOAD_REPORT
- FILL_FORM
- UPLOAD_FILE
- READ_TABLE
- SEND_EMAIL
- DELETE_CUSTOMER

Return ONLY valid JSON matching this structure:

{
    "intent": "<one of the supported intents>",
    "entities": {
        "<entity_name>": "<entity_value>"
    }
}

IMPORTANT ENTITY NAMES:

For ADD_CUSTOMER:
- customer_name
- phone_number

For ADD_PRODUCT:
- product_name
- category
- price
- stock
- status

For FILL_FORM:
- customer_name
- phone_number

For DELETE_CUSTOMER:
- customer_name

For UPDATE_PRODUCT:
- product_name
- price

For DOWNLOAD_REPORT:
- report_type
- date

For READ_TABLE:
- table

For UPLOAD_FILE:
- file_name

For SEND_EMAIL:
- recipient
- subject
- body

IMPORTANT RULES:

- Use the exact entity names listed above.
- For a customer name, ALWAYS use "customer_name", never "name".
- For a customer phone number, ALWAYS use "phone_number", never "phone".
- For a product, ALWAYS use "product_name", never "product".
- For a report type, ALWAYS use "report_type", never "report_name".
- Extract entities ONLY from the user's instruction.
- Never invent entity values.
- If an entity is not present in the instruction, do not include it.
- If the user says "Add a customer" without a name, do not invent a name.
- Return an empty entities object when no entities are present.
- Return only valid JSON.
- Do not include explanations or markdown.
- For ADD_PRODUCT, extract category and stock only when explicitly provided.
- Never invent category or stock.
- Status is optional.
""" + self._build_reference_prompt()

        raw_response = self.llm.chat(
            system_prompt=system_prompt,
            user_message=user_instruction,
        )

        result = IntentDetectionResponse.model_validate_json(raw_response)

        entities = dict(result.entities)

        aliases = {
            "name": "customer_name",
            "customer": "customer_name",
            "phone": "phone_number",
            "phone_no": "phone_number",
            "mobile": "phone_number",
            "mobile_number": "phone_number",
            "customer_phone": "phone_number",
            "customer_phone_number": "phone_number",
            "product": "product_name",
            "product_name": "product_name",
            "report_name": "report_type",
        }

        normalized_entities = {}

        for key, value in entities.items():
            canonical_key = aliases.get(key, key)

            if canonical_key not in normalized_entities:
                normalized_entities[canonical_key] = str(value).strip()

        instruction = user_instruction.strip()
        lower_instruction = instruction.lower()
        intent = result.intent.value

        if intent in {"ADD_CUSTOMER", "FILL_FORM"}:
            if "phone_number" not in normalized_entities:
                phone_match = re.search(
                    r"(?<!\d)(?:\+91[\s-]?)?([6-9]\d{9})(?!\d)",
                    instruction,
                )

                if phone_match:
                    normalized_entities["phone_number"] = (
                        phone_match.group(1)
                    )

            if "customer_name" not in normalized_entities:
                customer_name = self._extract_customer_name(
                    instruction
                )

                if customer_name:
                    normalized_entities["customer_name"] = (
                        customer_name
                    )

        elif intent == "DELETE_CUSTOMER":
            if "customer_name" not in normalized_entities:
                customer_name = self._extract_delete_customer_name(
                    instruction
                )

                if customer_name:
                    normalized_entities["customer_name"] = (
                        customer_name
                    )

        elif intent == "UPDATE_PRODUCT":
            if "price" not in normalized_entities:
                price_match = re.search(
                    r"(?:₹|\$|€|£)?\s*(\d+(?:\.\d+)?)",
                    instruction,
                )

                if price_match:
                    normalized_entities["price"] = (
                        price_match.group(1)
                    )

            if "product_name" not in normalized_entities:
                product_name = self._extract_product_name(
                    instruction
                )

                if product_name:
                    normalized_entities["product_name"] = (
                        product_name
                    )

        elif intent == "DOWNLOAD_REPORT":
            if "report_type" not in normalized_entities:
                report_type = self._extract_report_type(
                    lower_instruction
                )

                if report_type:
                    normalized_entities["report_type"] = (
                        report_type
                    )

            if "date" not in normalized_entities:
                date = self._extract_report_date(
                    lower_instruction
                )

                if date:
                    normalized_entities["date"] = date

        return result.model_copy(
            update={
                "entities": normalized_entities
            }
        )

    @staticmethod
    def _extract_customer_name(instruction: str) -> str | None:
        patterns = [
            r"\bcustomer\s+(?:called|named)\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"(?=\s+(?:with|and|mobile|phone|number)\b|$)",

            r"\b(?:add|create|register)\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"\s+as\s+(?:a\s+)?customer\b",

            r"\b(?:add|create|register)\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"\s+with\s+"
            r"(?:phone|mobile|number)\b",

            r"\bcustomer\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"\s+(?:add|create)\b",

            r"^([A-Za-z][A-Za-z .'-]*?)"
            r"\s+ka\s+customer\b",

            r"\bmake\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"\s+a\s+customer\b",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                instruction,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            name = match.group(1).strip(" ,.-")

            if name.lower() in {
                "a",
                "a customer",
                "the customer",
                "customer",
            }:
                continue

            return name

        return None

    @staticmethod
    def _extract_delete_customer_name(
        instruction: str,
    ) -> str | None:
        patterns = [
            r"\b(?:delete|remove)\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"(?=\s+(?:from|in|on|customer|customers|the)\b|$)",

            r"\b(?:delete|remove)\s+"
            r"([A-Za-z][A-Za-z .'-]*?)"
            r"\s+from\b",

            r"\b([A-Za-z][A-Za-z .'-]*?)"
            r"\s+ko\s+"
            r"(?:customers?|customer\s+database)"
            r"(?:\s+se)?\s+"
            r"(?:hatao|hata\s+do|remove\s+kar[o]?)\b",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                instruction,
                flags=re.IGNORECASE,
            )

            if match:
                name = match.group(1).strip(" ,.-")

                if name.lower() not in {
                    "customer",
                    "customers",
                    "the customer",
                }:
                    return name

        return None

    @staticmethod
    def _extract_product_name(
        instruction: str,
    ) -> str | None:
        patterns = [
            r"\b(?:set|change|update|make)\s+"
            r"(?:the\s+)?"
            r"([A-Za-z][A-Za-z0-9 .'-]*?)"
            r"\s+(?:ka\s+)?price\b",

            r"\b([A-Za-z][A-Za-z0-9 .'-]*?)"
            r"\s+ka\s+price\b",

            r"\bprice\s+"
            r"(?:₹|\$|€|£)?\s*\d+(?:\.\d+)?"
            r"\s+(?:as\s+the\s+price\s+)?for\s+"
            r"([A-Za-z][A-Za-z0-9 .'-]*)\s*$",

            r"\bprice\s+"
            r"(?:₹|\$|€|£)?\s*\d+(?:\.\d+)?"
            r".*?\bfor\s+"
            r"([A-Za-z][A-Za-z0-9 .'-]*)"
            r"\s*$",

            r"\bfor\s+"
            r"([A-Za-z][A-Za-z0-9 .'-]*)"
            r"\s*$",
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                instruction,
                flags=re.IGNORECASE,
            )

            if not match:
                continue

            product = match.group(1).strip(" ,.-")

            if product.lower() in {
                "the",
                "a",
                "product",
                "customer",
            }:
                continue

            return product

        return None

    @staticmethod
    def _extract_report_type(
        instruction: str,
    ) -> str | None:
        report_types = [
            ("sales", "sales report"),
            ("monthly", "monthly report"),
            ("daily", "daily report"),
            ("inventory", "inventory report"),
            ("weekly", "weekly report"),
        ]

        for keyword, canonical in report_types:
            if keyword in instruction:
                return canonical

        return None

    @staticmethod
    def _extract_report_date(
        instruction: str,
    ) -> str | None:
        direct_dates = [
            "today",
            "tomorrow",
            "yesterday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "last week",
            "this week",
            "next week",
        ]

        for date in direct_dates:
            if date in instruction:
                return date

        if re.search(r"\baaj\b|आज", instruction):
            return "today"

        if re.search(r"\bkal\b|कल", instruction):
            return "yesterday"

        return None