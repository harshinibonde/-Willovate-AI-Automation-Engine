import csv
import json
import random
import time
from pathlib import Path

from willovate.intent_detector import IntentDetector
from willovate.entity_normalizer import EntityNormalizer
from willovate.missing_info_handler import MissingInfoHandler
from willovate.workflow_generator import WorkflowGenerator
from willovate.validator import WorkflowValidator

DATASET_PATH = Path(__file__).parent / "dataset" / "willovate_evaluation_dataset.csv"
REPORT_PATH = Path(__file__).parent / "evaluation_report.json"
RANDOM_SEED = 42
EVAL_RATIO = 0.20
MAX_RETRIES = 5
RETRY_WAIT = 15

SUPPORTED_ACTIONS = {
    "OPEN_URL",
    "OPEN_PAGE",
    "CLICK",
    "ENTER_TEXT",
    "SELECT_OPTION",
    "UPLOAD_FILE",
    "DOWNLOAD_FILE",
    "READ_TEXT",
    "READ_TABLE",
    "SCROLL",
    "WAIT",
    "SUBMIT",
    "TAKE_SCREENSHOT",
    "DELETE",
}


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


def parse_json(value, default):
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def split_dataset(dataset):
    data = dataset.copy()
    random.Random(RANDOM_SEED).shuffle(data)
    eval_size = int(len(data) * EVAL_RATIO)
    return data[eval_size:], data[:eval_size]


def normalize_workflow(workflow):
    if isinstance(workflow, dict):
        workflow = workflow.get("steps", [])
    if not isinstance(workflow, list):
        return []

    normalized = []

    for step in workflow:
        if not isinstance(step, dict):
            continue

        action = step.get("action")

        if hasattr(action, "value"):
            action = action.value

        normalized.append({
            "action": action,
            "target": step.get("target"),
            "value": step.get("value"),
        })

    return normalized


def workflow_matches(expected, predicted):
    expected = normalize_workflow(expected)
    predicted = normalize_workflow(predicted)

    if not expected or not predicted:
        return expected == predicted

    predicted_set = {
        (
            step.get("action"),
            step.get("target"),
            step.get("value"),
        )
        for step in predicted
    }

    for expected_step in expected:
        expected_key = (
            expected_step.get("action"),
            expected_step.get("target"),
            expected_step.get("value"),
        )

        if expected_key not in predicted_set:
            return False

    return True


def get_actions(workflow):
    workflow = normalize_workflow(workflow)
    return [
        step.get("action")
        for step in workflow
        if step.get("action")
    ]


def calculate_unsupported_actions(workflow):
    actions = get_actions(workflow)
    return [
        action
        for action in actions
        if action not in SUPPORTED_ACTIONS
    ]


def calculate_hallucinated_steps(expected_workflow, predicted_workflow):
    expected = normalize_workflow(expected_workflow)
    predicted = normalize_workflow(predicted_workflow)

    expected_actions = {
        step.get("action")
        for step in expected
    }

    hallucinated = []

    for step in predicted:
        action = step.get("action")

        if action not in SUPPORTED_ACTIONS:
            hallucinated.append(step)
            continue

        if action not in expected_actions:
            continue

    return hallucinated


def detect_with_retry(detector, instruction):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return detector.detect(instruction)

        except Exception as error:
            error_text = str(error)

            if (
                "429" not in error_text
                and "rate_limit_exceeded" not in error_text
                and "Rate limit reached" not in error_text
                and "Too Many Requests" not in error_text
            ):
                raise

            if attempt == MAX_RETRIES:
                raise

            print(
                f"Rate limit reached. "
                f"Waiting {RETRY_WAIT}s before retry "
                f"({attempt}/{MAX_RETRIES})..."
            )

            time.sleep(RETRY_WAIT)

    raise RuntimeError("Detection failed after retries.")


def evaluate():
    full_dataset = load_dataset()
    development_set, eval_set = split_dataset(full_dataset)
    dataset = eval_set

    detector = IntentDetector()
    normalizer = EntityNormalizer()
    missing_handler = MissingInfoHandler()
    generator = WorkflowGenerator()
    validator = WorkflowValidator()

    total = len(dataset)

    intent_correct = 0
    entity_correct = 0
    clarification_correct = 0
    clarification_total = 0

    workflow_total = 0
    workflow_valid = 0
    workflow_generation_failed = 0
    workflow_validation_failed = 0
    workflow_generation_correct = 0

    json_valid_total = 0
    json_valid_count = 0

    unsupported_action_count = 0
    unsupported_action_total = 0

    hallucination_count = 0
    hallucination_total = 0

    results = []

    for index, example in enumerate(dataset, start=1):
        instruction = example["instruction"]
        expected_intent = example["expected_intent"]
        expected_entities = parse_json(
            example["expected_entities"],
            {},
        )
        expected_workflow = parse_json(
            example["expected_workflow"],
            [],
        )
        missing_fields = parse_json(
            example["missing_fields"],
            [],
        )

        expected_clarification = len(missing_fields) > 0

        print(f"\n[{index}/{total}] {instruction}")

        try:
            prediction = detect_with_retry(
                detector,
                instruction,
            )

            normalized_entities = normalizer.normalize(
                prediction.intent.value,
                prediction.entities,
            )

            prediction = prediction.model_copy(
                update={
                    "entities": normalized_entities
                }
            )

            predicted_intent = prediction.intent.value
            predicted_entities = prediction.entities

            intent_match = (
                predicted_intent == expected_intent
            )

            entity_match = (
                predicted_entities == expected_entities
            )

            if intent_match:
                intent_correct += 1

            if entity_match:
                entity_correct += 1

            clarification = missing_handler.check(
                prediction
            )

            predicted_clarification = (
                clarification.needs_clarification
            )

            clarification_match = (
                predicted_clarification
                == expected_clarification
            )

            clarification_total += 1

            if clarification_match:
                clarification_correct += 1

            workflow_is_valid = None
            workflow_data = None
            validation_errors = []
            workflow_generation_error = None
            workflow_match = None
            json_valid = None
            unsupported_actions = []
            hallucinated_steps = []

            if not expected_clarification:
                workflow_total += 1

                try:
                    workflow = generator.generate(
                        prediction
                    )

                    workflow_data = workflow.model_dump()

                    json.dumps(
                        workflow_data,
                        ensure_ascii=False,
                    )

                    json_valid = True
                    json_valid_count += 1

                except Exception as error:
                    workflow_generation_failed += 1
                    workflow_generation_error = str(error)
                    workflow_is_valid = False
                    json_valid = False

                json_valid_total += 1

                if workflow_data is not None:
                    predicted_steps = workflow_data.get(
                        "steps",
                        [],
                    )

                    workflow_match = workflow_matches(
                        expected_workflow,
                        predicted_steps,
                    )

                    if workflow_match:
                        workflow_generation_correct += 1

                    unsupported_actions = (
                        calculate_unsupported_actions(
                            predicted_steps
                        )
                    )

                    if unsupported_actions:
                        unsupported_action_count += 1

                    unsupported_action_total += 1

                    hallucinated_steps = (
                        calculate_hallucinated_steps(
                            expected_workflow,
                            predicted_steps,
                        )
                    )

                    if hallucinated_steps:
                        hallucination_count += 1

                    hallucination_total += 1

                    if workflow_is_valid is None:
                        (
                            workflow_is_valid,
                            validation_errors,
                        ) = validator.validate(
                            workflow
                        )

                        if workflow_is_valid:
                            workflow_valid += 1
                        else:
                            workflow_validation_failed += 1

            print(
                "Expected intent:",
                expected_intent,
            )

            print(
                "Predicted intent:",
                predicted_intent,
            )

            print(
                "Expected entities:",
                expected_entities,
            )

            print(
                "Predicted entities:",
                predicted_entities,
            )

            print(
                "Expected clarification:",
                expected_clarification,
            )

            print(
                "Predicted clarification:",
                predicted_clarification,
            )

            if workflow_is_valid is not None:
                print(
                    "Workflow valid:",
                    workflow_is_valid,
                )

            if workflow_match is not None:
                print(
                    "Workflow generation match:",
                    workflow_match,
                )

            if unsupported_actions:
                print(
                    "Unsupported actions:",
                    unsupported_actions,
                )

            if hallucinated_steps:
                print(
                    "Hallucinated steps:",
                    hallucinated_steps,
                )

            results.append({
                "instruction": instruction,
                "expected_intent": expected_intent,
                "predicted_intent": predicted_intent,
                "expected_entities": expected_entities,
                "predicted_entities": predicted_entities,
                "expected_workflow": expected_workflow,
                "predicted_workflow": workflow_data,
                "expected_clarification": expected_clarification,
                "predicted_clarification": predicted_clarification,
                "workflow_valid": workflow_is_valid,
                "workflow_generation_match": workflow_match,
                "json_valid": json_valid,
                "unsupported_actions": unsupported_actions,
                "hallucinated_steps": hallucinated_steps,
                "validation_errors": validation_errors,
                "workflow_generation_error": workflow_generation_error,
                "intent_correct": intent_match,
                "entity_correct": entity_match,
                "clarification_correct": clarification_match,
            })

        except Exception as error:
            print(
                "PIPELINE ERROR:",
                error,
            )

            results.append({
                "instruction": instruction,
                "expected_intent": expected_intent,
                "expected_entities": expected_entities,
                "expected_workflow": expected_workflow,
                "expected_clarification": expected_clarification,
                "error": str(error),
                "intent_correct": False,
                "entity_correct": False,
                "clarification_correct": False,
                "workflow_valid": False,
                "workflow_generation_match": False,
                "json_valid": False,
            })

    intent_accuracy = (
        intent_correct / total
        if total
        else 0
    )

    entity_accuracy = (
        entity_correct / total
        if total
        else 0
    )

    clarification_accuracy = (
        clarification_correct / clarification_total
        if clarification_total
        else 0
    )

    workflow_validity = (
        workflow_valid / workflow_total
        if workflow_total
        else 0
    )

    workflow_generation_accuracy = (
        workflow_generation_correct / workflow_total
        if workflow_total
        else 0
    )

    json_validity = (
        json_valid_count / json_valid_total
        if json_valid_total
        else 0
    )

    unsupported_action_rate = (
        unsupported_action_count / unsupported_action_total
        if unsupported_action_total
        else 0
    )

    hallucination_rate = (
        hallucination_count / hallucination_total
        if hallucination_total
        else 0
    )

    entity_failures = [
        result
        for result in results
        if not result.get(
            "entity_correct",
            False,
        )
    ]

    clarification_failures = [
        result
        for result in results
        if not result.get(
            "clarification_correct",
            False,
        )
    ]

    workflow_failures = [
        result
        for result in results
        if result.get(
            "workflow_valid"
        ) is False
    ]

    print("\n" + "=" * 60)
    print("WILLOVATE MODEL EVALUATION")
    print("=" * 60)
    print(
        f"Total dataset examples:       "
        f"{len(full_dataset)}"
    )
    print(
        f"Development examples:         "
        f"{len(development_set)}"
    )
    print(
        f"Evaluation examples:          "
        f"{len(eval_set)}"
    )
    print(
        f"Intent accuracy:               "
        f"{intent_accuracy:.2%}"
    )
    print(
        f"Entity accuracy:               "
        f"{entity_accuracy:.2%}"
    )
    print(
        f"Missing-info accuracy:         "
        f"{clarification_accuracy:.2%}"
    )
    print(
        f"Workflow generation accuracy:  "
        f"{workflow_generation_accuracy:.2%}"
    )
    print(
        f"JSON validity:                 "
        f"{json_validity:.2%}"
    )
    print(
        f"Workflow validation:           "
        f"{workflow_validity:.2%}"
    )
    print(
        f"Unsupported-action rate:       "
        f"{unsupported_action_rate:.2%}"
    )
    print(
        f"Hallucination rate:            "
        f"{hallucination_rate:.2%}"
    )
    print("=" * 60)

    print("\n" + "=" * 60)
    print("WORKFLOW BREAKDOWN")
    print("=" * 60)
    print(
        f"Workflow attempts:             "
        f"{workflow_total}"
    )
    print(
        f"Valid workflows:               "
        f"{workflow_valid}"
    )
    print(
        f"Generation failures:           "
        f"{workflow_generation_failed}"
    )
    print(
        f"Validation failures:           "
        f"{workflow_validation_failed}"
    )
    print("=" * 60)

    print("\n" + "=" * 60)
    print("FAILURE ANALYSIS")
    print("=" * 60)

    print(
        f"\nEntity failures: "
        f"{len(entity_failures)}"
    )

    for result in entity_failures:
        print(
            f"\n{result['instruction']}"
        )
        print(
            "Expected:",
            result["expected_entities"],
        )
        print(
            "Predicted:",
            result.get("predicted_entities"),
        )

    print(
        f"\nClarification failures: "
        f"{len(clarification_failures)}"
    )

    for result in clarification_failures:
        print(
            f"\n{result['instruction']}"
        )
        print(
            "Expected:",
            result["expected_clarification"],
        )
        print(
            "Predicted:",
            result.get("predicted_clarification"),
        )

    print(
        f"\nWorkflow failures: "
        f"{len(workflow_failures)}"
    )

    for result in workflow_failures:
        print(
            f"\n{result['instruction']}"
        )

        if result.get(
            "workflow_generation_error"
        ):
            print(
                "Generation error:",
                result[
                    "workflow_generation_error"
                ],
            )
        else:
            print(
                "Validation errors:",
                result.get(
                    "validation_errors",
                    [],
                ),
            )

    report = {
        "dataset": str(DATASET_PATH),
        "random_seed": RANDOM_SEED,
        "eval_ratio": EVAL_RATIO,
        "total_examples": len(full_dataset),
        "development_examples": len(
            development_set
        ),
        "evaluation_examples": len(
            eval_set
        ),
        "metrics": {
            "intent_accuracy": intent_accuracy,
            "entity_accuracy": entity_accuracy,
            "missing_information_accuracy": clarification_accuracy,
            "workflow_generation_accuracy": workflow_generation_accuracy,
            "json_validity": json_validity,
            "workflow_validation_rate": workflow_validity,
            "unsupported_action_rate": unsupported_action_rate,
            "hallucination_rate": hallucination_rate,
        },
        "workflow_breakdown": {
            "workflow_attempts": workflow_total,
            "valid_workflows": workflow_valid,
            "generation_failures": workflow_generation_failed,
            "validation_failures": workflow_validation_failed,
        },
        "counts": {
            "intent_correct": intent_correct,
            "entity_correct": entity_correct,
            "clarification_correct": clarification_correct,
            "clarification_total": clarification_total,
            "workflow_generation_correct": workflow_generation_correct,
            "workflow_valid": workflow_valid,
            "workflow_total": workflow_total,
            "json_valid_count": json_valid_count,
            "json_valid_total": json_valid_total,
            "unsupported_action_count": unsupported_action_count,
            "unsupported_action_total": unsupported_action_total,
            "hallucination_count": hallucination_count,
            "hallucination_total": hallucination_total,
        },
        "results": results,
    }

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        f"\nReport saved to: "
        f"{REPORT_PATH}"
    )


if __name__ == "__main__":
    evaluate()