from willovate.intent_detector import IntentDetector
from willovate.missing_info_handler import MissingInfoHandler
from willovate.workflow_generator import WorkflowGenerator
from willovate.validator import WorkflowValidator
from willovate.risk_classifier import RiskClassifier
from willovate.automation_runner import AutomationRunner


def main():
    instruction = input("\nWhat should Willovate do?\n> ").strip()

    if not instruction:
        print("No instruction provided.")
        return

    print("\n[1/5] Detecting intent...")

    detector = IntentDetector()
    intent_result = detector.detect(instruction)

    print(f"Intent: {intent_result.intent.value}")
    print(f"Entities: {intent_result.entities}")

    print("\n[2/5] Checking required information...")

    missing_handler = MissingInfoHandler()
    clarification = missing_handler.check(intent_result)

    if clarification.needs_clarification:
        print("\nClarification required:")
        print(clarification.question)
        return

    print("Required information: COMPLETE")

    print("\n[3/5] Generating workflow...")

    generator = WorkflowGenerator()
    workflow = generator.generate(intent_result)

    print("\nGenerated workflow:")

    for index, step in enumerate(
        workflow.steps,
        start=1,
    ):
        print(
            f"{index}. "
            f"{step.action.value} | "
            f"{step.target} | "
            f"{step.value}"
        )

    print("\n[4/5] Validating and checking risk...")

    validator = WorkflowValidator()
    valid, errors = validator.validate(workflow)

    if not valid:
        print("\nWorkflow validation failed:")

        for error in errors:
            print(f"- {error}")

        return

    print("Workflow validation: PASSED")

    risk_classifier = RiskClassifier()
    risk = risk_classifier.classify(workflow)

    print(f"Risky workflow: {risk['is_risky']}")
    print(f"Risk types: {risk['risk_types']}")

    if risk["requires_confirmation"]:
        print("\nConfirmation required.")
        print(
            "This workflow contains a high-risk action: "
            + ", ".join(risk["risk_types"])
        )

        confirmation = input(
            "Do you want to continue? (yes/no): "
        ).strip().lower()

        if confirmation not in {"yes", "y"}:
            print("Execution cancelled.")
            return

    print("\n[5/5] Executing workflow...")

    runner = AutomationRunner()
    results = runner.run(workflow)

    print("\nAutomation results:")

    for result in results:
        print(result)

    print("\nWillovate execution completed.")


if __name__ == "__main__":
    main()