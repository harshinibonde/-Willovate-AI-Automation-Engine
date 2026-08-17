from willovate.schemas import ActionType, Workflow


class RiskClassifier:
    def classify(self, workflow: Workflow) -> dict:
        risk_types = []

        for step in workflow.steps:
            if step.action == ActionType.DELETE:
                if "delete" not in risk_types:
                    risk_types.append("delete")

            elif (
                step.action == ActionType.CLICK
                and step.target == "#send-email"
            ):
                if "send_email" not in risk_types:
                    risk_types.append("send_email")

        return {
            "is_risky": len(risk_types) > 0,
            "risk_types": risk_types,
            "requires_confirmation": len(risk_types) > 0,
        }