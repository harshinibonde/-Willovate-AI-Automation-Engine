from willovate.intent_detector import IntentDetector
from willovate.missing_info_handler import MissingInfoHandler
from willovate.workflow_generator import WorkflowGenerator
from willovate.validator import WorkflowValidator
from willovate.risk_classifier import RiskClassifier
from willovate.automation_runner import AutomationRunner


def main():

    instruction = (
        "Add Pankaj Koche as a customer "
        "with phone number 9876543210"
    )

    # 1. Intent + entities
    detector = IntentDetector()
    intent_result = detector.detect(instruction)

    print("\nIntent:")
    print(intent_result)

    # 2. Missing information
    handler = MissingInfoHandler()
    clarification = handler.check(intent_result)

    if clarification.needs_clarification:
        print("\nClarification:")
        print(clarification)
        return

    # 3. Generate workflow
    generator = WorkflowGenerator()
    workflow = generator.generate(intent_result)

    print("\nGenerated workflow:")
    print(workflow.model_dump_json(indent=2))

    # 4. Validate
    validator = WorkflowValidator()
    valid, errors = validator.validate(workflow)

    if not valid:
        print("\nValidation failed:")
        print(errors)
        return

    print("\nWorkflow validation: PASSED")

    # 5. Risk check
    risk_classifier = RiskClassifier()
    risk = risk_classifier.classify(workflow)

    print("\nRisk:")
    print(risk)

    if risk["requires_confirmation"]:
        print("Confirmation required.")
        return

    # 6. Execute
    runner = AutomationRunner()
    results = runner.run(workflow)
    
    expected_name = "Pankaj Koche"

    verified = any(
        expected_name in result
        for result in results
    )

    print("\nFinal verification:", "PASSED" if verified else "FAILED")

    print("\nExecution results:")
    print(results)


if __name__ == "__main__":
    main()