from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from willovate.intent_detector import IntentDetector
from willovate.missing_info_handler import MissingInfoHandler
from willovate.workflow_generator import WorkflowGenerator
from willovate.multi_step_planner import MultiStepPlanner
from willovate.validator import WorkflowValidator
from willovate.risk_classifier import RiskClassifier
from willovate.entity_normalizer import EntityNormalizer
from willovate.automation_runner import AutomationRunner

entity_normalizer = EntityNormalizer()
automation_runner = AutomationRunner()

app = FastAPI(
    title="Willovate AI Automation Engine",
    version="1.0.0",
)

intent_detector = IntentDetector()
missing_info_handler = MissingInfoHandler()
workflow_generator = WorkflowGenerator()
multi_step_planner = MultiStepPlanner()
workflow_validator = WorkflowValidator()
risk_classifier = RiskClassifier()


class WorkflowRequest(BaseModel):
    instruction: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-workflow")
def generate_workflow(request: WorkflowRequest):

    instruction = request.instruction.strip()

    if not instruction:
        raise HTTPException(
            status_code=400,
            detail="Instruction cannot be empty.",
        )

    # Intent + entities
    intent_result = intent_detector.detect(instruction)
    normalized_entities = entity_normalizer.normalize(
        intent_result.intent.value,
        intent_result.entities,
    )
    intent_result = intent_result.model_copy(
        update={
            "entities": normalized_entities
        }
    )

    # Missing information
    clarification = missing_info_handler.check(intent_result)

    if clarification.needs_clarification:
        return {
            "status": "needs_clarification",
            "intent": intent_result.intent.value,
            "entities": intent_result.entities,
            "clarification": clarification.model_dump(),
        }

    # Detect compound instructions
    compound_keywords = [
        " and ",
        " then ",
        " after that ",
        " followed by ",
    ]

    is_compound = any(
        keyword in instruction.lower()
        for keyword in compound_keywords
    )

    # Generate workflow
    if is_compound:
        workflow = multi_step_planner.plan(instruction)
    else:
        workflow = workflow_generator.generate(intent_result)

    # Validate
    valid, errors = workflow_validator.validate(workflow)

    if not valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Workflow validation failed.",
                "errors": errors,
            },
        )

    # Risk classification
    risk = risk_classifier.classify(workflow)

    return {
        "status": "success",
        "intent": intent_result.intent.value,
        "entities": intent_result.entities,
        "workflow": workflow.model_dump(),
        "risk": risk,
    }
    
@app.post("/execute-workflow")
def execute_workflow(request: WorkflowRequest):

    instruction = request.instruction.strip()

    if not instruction:
        raise HTTPException(
            status_code=400,
            detail="Instruction cannot be empty.",
        )

    # 1. Detect intent and entities
    intent_result = intent_detector.detect(
        instruction
    )

    # 2. Normalize entities
    normalized_entities = entity_normalizer.normalize(
        intent_result.intent.value,
        intent_result.entities,
    )

    intent_result = intent_result.model_copy(
        update={
            "entities": normalized_entities
        }
    )

    # 3. Check missing information
    clarification = missing_info_handler.check(
        intent_result
    )

    if clarification.needs_clarification:
        return {
            "status": "needs_clarification",
            "intent": intent_result.intent.value,
            "entities": intent_result.entities,
            "clarification": clarification.model_dump(),
        }

    # 4. Generate workflow
    workflow = workflow_generator.generate(
        intent_result
    )

    # 5. Validate workflow
    valid, errors = workflow_validator.validate(
        workflow
    )

    if not valid:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Workflow validation failed.",
                "errors": errors,
            },
        )

    # 6. Risk classification
    risk = risk_classifier.classify(
        workflow
    )

    # 7. Stop risky workflows for now
    if risk["requires_confirmation"]:
        return {
            "status": "confirmation_required",
            "intent": intent_result.intent.value,
            "entities": intent_result.entities,
            "workflow": workflow.model_dump(),
            "risk": risk,
        }

    # 8. Execute with Playwright
    execution_results = automation_runner.run(
        workflow
    )

    return {
        "status": "executed",
        "intent": intent_result.intent.value,
        "entities": intent_result.entities,
        "workflow": workflow.model_dump(),
        "risk": risk,
        "execution_results": execution_results,
    }