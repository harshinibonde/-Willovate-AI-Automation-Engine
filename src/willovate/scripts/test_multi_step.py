from willovate.multi_step_planner import MultiStepPlanner


def main():

    instruction = (
        "Open the CRM, add Pankaj Koche with phone "
        "9876543210, save the customer, and verify "
        "that Pankaj Koche appears in the table."
    )

    planner = MultiStepPlanner()
    workflow = planner.plan(instruction)

    print("\nGenerated Multi-Step Workflow:")
    print(workflow.model_dump_json(indent=2))


if __name__ == "__main__":
    main()