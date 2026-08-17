from willovate.intent_detector import IntentDetector

def main():
    detector =  IntentDetector()
    
    result = detector.detect(
        "Add Rahul as a customer with phone number 9876543210"
    )
    
    print(result)
    print()
    print("Intent: ", result.intent)
    print("Entities: ", result.entities)
    
if __name__ == "__main__":
    main()
    
    