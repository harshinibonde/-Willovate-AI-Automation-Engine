import csv
import json
import random
from pathlib import Path


DATASET_PATH = (
    Path(__file__).parent
    / "dataset"
    / "willovate_evaluation_dataset.csv"
)

OUTPUT_PATH = (
    Path(__file__).parent
    / "reference_examples.json"
)

RANDOM_SEED = 123
EVAL_SEED = 42
EVAL_RATIO = 0.20

INTENTS = [
    "ADD_CUSTOMER",
    "UPDATE_PRODUCT",
    "DOWNLOAD_REPORT",
    "FILL_FORM",
    "UPLOAD_FILE",
    "READ_TABLE",
    "SEND_EMAIL",
    "DELETE_CUSTOMER",
]


def load_dataset():
    with open(
        DATASET_PATH,
        "r",
        encoding="utf-8-sig",
    ) as file:
        return list(csv.DictReader(file))


def split_dataset(dataset):
    data = dataset.copy()

    random.Random(EVAL_SEED).shuffle(data)

    eval_size = int(len(data) * EVAL_RATIO)

    evaluation_set = data[:eval_size]
    development_set = data[eval_size:]

    return development_set, evaluation_set


def parse_json(value):
    if not value:
        return {}

    return json.loads(value)


def get_field(row, *names):
    for name in names:
        if name in row:
            return row[name]

    return ""


def select_references(development_set):
    rng = random.Random(RANDOM_SEED)

    references = []

    for intent in INTENTS:
        candidates = [
            row
            for row in development_set
            if get_field(
                row,
                "expected_intent",
                "intent",
            ) == intent
        ]

        rng.shuffle(candidates)

        selected = candidates[:5]

        if len(selected) < 5:
            print(
                f"WARNING: only {len(selected)} examples "
                f"found for {intent}"
            )

        for row in selected:
            references.append(
                {
                    "instruction": row["instruction"],
                    "intent": get_field(
                        row,
                        "expected_intent",
                        "intent",
                    ),
                    "entities": parse_json(
                        get_field(
                            row,
                            "expected_entities",
                            "entities_json",
                        )
                    ),
                }
            )

    return references


def main():
    dataset = load_dataset()

    development_set, evaluation_set = split_dataset(
        dataset
    )

    references = select_references(
        development_set
    )

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            references,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 50)
    print("REFERENCE DATASET CREATED")
    print("=" * 50)

    print(
        f"Full dataset:       {len(dataset)}"
    )

    print(
        f"Development set:    {len(development_set)}"
    )

    print(
        f"Evaluation set:     {len(evaluation_set)}"
    )

    print(
        f"Reference examples: {len(references)}"
    )

    print(
        f"Saved to:            {OUTPUT_PATH}"
    )

    print("=" * 50)


if __name__ == "__main__":
    main()