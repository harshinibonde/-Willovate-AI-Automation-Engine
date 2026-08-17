from willovate.schemas import (
    ClarificationResponse,
    IntentDetectionResponse,
)


REQUIRED_FIELDS = {
    "ADD_CUSTOMER": [
        "customer_name",
        "phone_number",
    ],
    "ADD_PRODUCT": [
    "product_name",
    "category",
    "price",
    "stock",
    ],
    "UPDATE_PRODUCT": [
        "product_name",
        "price",
    ],
    "DOWNLOAD_REPORT": [
        "date",
    ],
    "DELETE_CUSTOMER": [
        "customer_name",
    ],
    "UPLOAD_FILE": [
        "file_name",
    ],
    "SEND_EMAIL": [
    "recipient",
    "subject",
    "body",
    ],
    "FILL_FORM": [
    "customer_name",
    "phone_number",
    ],
}


class MissingInfoHandler:

    def check(
        self,
        result: IntentDetectionResponse,
    ) -> ClarificationResponse:

        required_fields = REQUIRED_FIELDS.get(
            result.intent.value,
            []
        )

        missing_fields = [
            field
            for field in required_fields
            if field not in result.entities
        ]

        if not missing_fields:
            return ClarificationResponse(
                needs_clarification=False
            )

        question = self._build_question(
            result,
            missing_fields
        )

        return ClarificationResponse(
            needs_clarification=True,
            question=question,
            missing_fields=missing_fields,
        )
        
    def _build_question(
        self,
        result: IntentDetectionResponse,
        missing_fields: list[str],
    ) -> str:

        if (
            result.intent.value == "ADD_CUSTOMER"
            and missing_fields == ["phone_number"]
        ):
            customer_name = result.entities.get(
                "customer_name",
                "the customer"
            )

            return f"What is {customer_name}'s phone number?"

        if (
            result.intent.value == "ADD_CUSTOMER"
            and missing_fields == [
                "customer_name",
                "phone_number",
            ]
        ):
            return "What is the customer's name and phone number?"

        return (
            "Please provide the following information: "
            + ", ".join(missing_fields)
        )    