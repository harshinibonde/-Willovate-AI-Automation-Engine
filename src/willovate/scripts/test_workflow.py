from willovate.intent_detector import IntentDetector
from willovate.missing_info_handler import MissingInfoHandler
from willovate.workflow_generator import WorkflowGenerator


instruction = "Add Rahul as a customer with phone number 9876543210"

detector = IntentDetector()
result = detector.detect(instruction)

handler = MissingInfoHandler()
clarification = handler.check(result)

if not clarification.needs_clarification:
    generator = WorkflowGenerator()
    workflow = generator.generate(result)
    print(workflow.model_dump_json(indent=2))
else:
    print(clarification)