from willovate.llm_client import LLMClient

def main():
    client = LLMClient()
    result = client.chat(
        system_prompt="You are a helpful assistant.",
        user_message="Add Rahul with phone number 9876543210",
    )
    print(result)

if __name__ == "__main__":
    main()