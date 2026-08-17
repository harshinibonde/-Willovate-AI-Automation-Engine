import re


class EntityNormalizer:

    KEY_ALIASES = {
        "name": "customer_name",
        "customer": "customer_name",

        "phone": "phone_number",
        "phone_no": "phone_number",
        "mobile": "phone_number",
        "mobile_number": "phone_number",
        "customer_phone": "phone_number",
        "customer_phone_number": "phone_number",

        "product": "product_name",
    
        "new_price": "price",
        "product_price": "price",

        "report_date": "date",
        "timeframe": "date",
        "time_period": "date",

        "report_name": "report_type",

        "table_name": "table",

        "file": "file_name",
    }

    VALUE_NORMALIZERS = {
        "date": {
            "aaj": "today",
            "आज": "today",
        }
    }
    
    INVALID_CUSTOMER_NAMES = {
        "customer",
        "a customer",
        "the customer",
        "customers",
}

    def normalize(self, intent: str, entities: dict) -> dict:
        normalized = {}

        for key, value in entities.items():

            canonical_key = self.KEY_ALIASES.get(
                key,
                key
            )

            value = str(value).strip()
            
            if canonical_key == "customer_name":
                if value.lower() in self.INVALID_CUSTOMER_NAMES:
                    continue

            # Remove currency symbol for price
            if canonical_key == "price":
                value = re.sub(r"^[₹$€£]\s*", "", value)

            # Normalize known values
            if canonical_key in self.VALUE_NORMALIZERS:
                value = self.VALUE_NORMALIZERS[
                    canonical_key
                ].get(value.lower(), value)

            normalized[canonical_key] = value

        return normalized