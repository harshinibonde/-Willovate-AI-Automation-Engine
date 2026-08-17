import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass(frozen=True)
class Settings:
    groq_api_key: str = ""
    model_name: str = "willovate-gpt-oss-20b-lora"
    temperature: float = 0.0
    max_tokens: int = 128
    fine_tuned_api_url: str = ""

    def validate(self) -> None:
        if not self.fine_tuned_api_url:
            raise ValueError(
                "FINE_TUNED_API_URL is missing. "
                "Add it to your .env file."
            )


def get_settings() -> Settings:
    settings = Settings(
        groq_api_key=os.environ.get("GROQ_API_KEY", ""),
        model_name=os.environ.get(
            "MODEL_NAME",
            "willovate-gpt-oss-20b-lora"
        ),
        temperature=float(
            os.environ.get("TEMPERATURE", "0.0")
        ),
        max_tokens=int(
            os.environ.get("MAX_TOKENS", "128")
        ),
        fine_tuned_api_url=os.environ.get(
            "FINE_TUNED_API_URL",
            ""
        ),
    )

    settings.validate()
    return settings