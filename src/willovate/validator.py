from willovate.schemas import ActionType, Workflow


REQUIRED_PARAMS = {
    ActionType.OPEN_URL: ["target"],
    ActionType.OPEN_PAGE: ["target"],
    ActionType.CLICK: ["target"],
    ActionType.ENTER_TEXT: ["target", "value"],
    ActionType.SELECT_OPTION: ["target", "value"],
    ActionType.UPLOAD_FILE: ["target", "value"],
    ActionType.DOWNLOAD_FILE: ["target"],
    ActionType.READ_TEXT: ["target"],
    ActionType.READ_TABLE: ["target"],
    ActionType.SCROLL: ["target"],
    ActionType.WAIT: ["target"],
    ActionType.SUBMIT: ["target"],
    ActionType.TAKE_SCREENSHOT: ["target"],
    ActionType.UPDATE_TEXT: ["target", "value"],
    ActionType.SET_ATTRIBUTE: ["target", "value"],
}


class WorkflowValidator:

    def validate(self, workflow: Workflow) -> tuple[bool, list[str]]:
        errors = []

        if not workflow.steps:
            errors.append("Workflow contains no steps.")
            return False, errors

        for index, step in enumerate(workflow.steps):

            required = REQUIRED_PARAMS.get(step.action, [])

            if "target" in required and not step.target:
                errors.append(
                    f"Step {index}: target is required."
                )

            if "value" in required and not step.value:
                errors.append(
                    f"Step {index}: value is required "
                    f"for {step.action.value}."
                )

        # Sample CRM semantic validation
        actions = [step.action for step in workflow.steps]

        if ActionType.ENTER_TEXT in actions:
            enter_targets = {
                step.target
                for step in workflow.steps
                if step.action == ActionType.ENTER_TEXT
            }

            if "#customer-name" in enter_targets:
                if "#phone-number" not in enter_targets:
                    errors.append(
                        "Customer workflow requires phone number."
                    )

        # SUBMIT should happen before READ_TABLE
        submit_indices = [
            i for i, step in enumerate(workflow.steps)
            if step.action == ActionType.SUBMIT
        ]

        read_table_indices = [
            i for i, step in enumerate(workflow.steps)
            if step.action == ActionType.READ_TABLE
        ]

        return len(errors) == 0, errors