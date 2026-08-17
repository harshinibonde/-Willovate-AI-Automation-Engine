from willovate.risk_classifier import RiskClassifier
from willovate.schemas import Workflow, WorkflowStep


def main():

    classifier = RiskClassifier()

    workflow = Workflow(
        steps=[
            WorkflowStep(
                action="DELETE",
                target="#customer",
                value="Rahul",
            )
        ]
    )

    result = classifier.classify(workflow)

    print("Risk result:")
    print(result)


if __name__ == "__main__":
    main()