import os
import requests
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        self.fine_tuned_api_url = os.getenv("FINE_TUNED_API_URL", "").strip()
        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_model = "openai/gpt-oss-120b"
        self.timeout = int(os.getenv("LLM_TIMEOUT", "60"))

    def chat(
        self,
        prompt: str = None,
        system_prompt: str = None,
        user_message: str = None,
    ) -> str:
        if user_message is not None:
            prompt = user_message

        if prompt is None:
            raise ValueError("No user prompt provided.")

        if self.fine_tuned_api_url:
            try:
                url = self.fine_tuned_api_url.rstrip("/") + "/api/generate"

                response = requests.post(
                    url,
                    json={
                        "prompt": prompt,
                        "system_prompt": system_prompt,
                    },
                    timeout=self.timeout,
                )
                response.raise_for_status()

                data = response.json()

                if isinstance(data, dict) and data.get("response") is not None:
                    return str(data["response"])

            except (
                requests.RequestException,
                ValueError,
                TypeError,
                KeyError,
            ):
                pass

        return self._groq_chat(prompt, system_prompt)

    def _groq_chat(self, prompt: str, system_prompt: str = None) -> str:
        if not self.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        messages = []

        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt,
            })

        messages.append({
            "role": "user",
            "content": prompt,
        })

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.groq_model,
                "messages": messages,
                "temperature": 0,
                "max_completion_tokens": 1024,
            },
            timeout=self.timeout,
        )

        if not response.ok:
            print("GROQ ERROR:")
            print(response.text)

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]