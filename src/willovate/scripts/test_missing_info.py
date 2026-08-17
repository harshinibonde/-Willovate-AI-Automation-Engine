from willovate.intent_detector import IntentDetector
from willovate.missing_info_handler import MissingInfoHandler


def main():
    detector = IntentDetector()
    handler = MissingInfoHandler()

    result = detector.detect(
        "Add Rahul as a customer"
    )

    print("Intent result:")
    print(result)

    clarification = handler.check(result)

    print("\nClarification result:")
    print(clarification)


if __name__ == "__main__":
    main()