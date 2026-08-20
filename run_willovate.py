from willovate.intent_detector import IntentDetector
from willovate.missing_info_handler import MissingInfoHandler
from willovate.workflow_generator import WorkflowGenerator
from willovate.validator import WorkflowValidator
from willovate.risk_classifier import RiskClassifier
from willovate.automation_runner import AutomationRunner


def main():
    try:
        instruction = input("\nWhat should Willovate do?\n> ").strip()
    except (EOFError, KeyboardInterrupt):
        return

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

    if "webpage_modification" in risk["risk_types"] or intent_result.intent.value in ("CUSTOMIZE_PAGE", "UPLOAD_IMAGE", "CREATE_OFFER"):
        print("\n" + "="*50)
        print("PROPOSED CHANGE PREVIEW")
        print("="*50)
        for step in workflow.steps:
            if step.action.value in ("UPDATE_TEXT", "SET_ATTRIBUTE", "UPLOAD_FILE", "ENTER_TEXT"):
                print(f"  • Action : {step.action.value}")
                print(f"    Target : {step.target}")
                print(f"    Value  : {step.value}")
        print("="*50)

    if risk["requires_confirmation"]:
        print("\nConfirmation required.")
        print(
            "This workflow contains a sensitive or high-risk action: "
            + ", ".join(risk["risk_types"])
        )

        try:
            confirmation = input(
                "Do you want to apply these changes? (yes/no): "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            confirmation = "yes"

        if confirmation not in {"yes", "y"}:
            print("Execution cancelled.")
            return

    print("\n[5/5] Executing workflow...")

    runner = AutomationRunner()
    results = runner.run(workflow)

    print("\nAutomation results:")

    for result in results:
        if isinstance(result, dict) and result.get("type") == "verification_result":
            vr = result["result"]
            print("\n--- VISUAL & DOM VERIFICATION ---")
            print(f"  DOM Verification : {vr.get('dom_result')}")
            print(f"  OCR Verification : {vr.get('ocr_result')}")
            print(f"  Combined Status  : {vr.get('combined')}")
            print(f"  Details          : {vr.get('details')}")
            print("---------------------------------\n")
        else:
            print(result)

    if runner.rollback_manager.has_rollback_history():
        last_change = runner.rollback_manager.get_last_change()
        print(f"\n[Rollback Available] Target: {last_change.target} | Original text: '{last_change.previous_value}'")
        try:
            undo = input("Do you want to undo / rollback this change? (yes/no): ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            undo = "no"
        if undo in {"yes", "y"}:
            print("Note: To execute rollback, keep browser open or run rollback engine.")
            print(f"Rollback recorded for {last_change.target} -> '{last_change.previous_value}'.")

    print("\nWillovate execution completed.")


if __name__ == "__main__":
    main()