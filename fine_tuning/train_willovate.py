import ast
import json
import random
from pathlib import Path

import pandas as pd

SEED = 42
TRAIN_SIZE = 320
EVAL_SIZE = 80

ROOT = Path(__file__).resolve().parents[1]

CSV_PATH = (
    ROOT
    / "src"
    / "willovate"
    / "dataset"
    / "willovate_evaluation_dataset.csv"
)

OUTPUT_DIR = ROOT / "fine_tuning" / "data"

SYSTEM_PROMPT = """You are Willovate, an AI automation engine.

Convert the user's natural-language instruction into a structured automation workflow.

Return ONLY valid JSON:

{
  "intent": "INTENT",
  "entities": {},
  "missing_fields": [],
  "risk_level": "low",
  "workflow": []
}

Supported intents:
ADD_CUSTOMER
UPDATE_PRODUCT
DOWNLOAD_REPORT
FILL_FORM
UPLOAD_FILE
READ_TABLE
SEND_EMAIL
DELETE_CUSTOMER

Supported actions:
OPEN_URL
OPEN_PAGE
CLICK
ENTER_TEXT
SELECT_OPTION
UPLOAD_FILE
DOWNLOAD_FILE
READ_TEXT
READ_TABLE
SCROLL
WAIT
SUBMIT
TAKE_SCREENSHOT
DELETE

Rules:
- Never invent information.
- Extract entities only from the user's instruction.
- If required information is missing, put it in missing_fields.
- Use only supported actions.
- Do not invent workflow steps.
- Preserve the user's requested order.
- Return valid JSON only.
- Do not include explanations or markdown.
"""


def parse_value(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    try:
        return json.loads(value)
    except Exception:
        pass

    try:
        return ast.literal_eval(value)
    except Exception:
        pass

    return value


def make_example(row):
    entities = parse_value(row["expected_entities"])
    workflow = parse_value(row["expected_workflow"])
    missing_fields = parse_value(row["missing_fields"])

    if not isinstance(entities, dict):
        entities = {}

    if not isinstance(workflow, list):
        workflow = []

    if not isinstance(missing_fields, list):
        missing_fields = []

    answer = {
        "intent": str(row["expected_intent"]).strip(),
        "entities": entities,
        "missing_fields": missing_fields,
        "risk_level": str(row["risk_level"]).strip(),
        "workflow": workflow
    }

    return {
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": str(row["instruction"]).strip()
            },
            {
                "role": "assistant",
                "content": json.dumps(
                    answer,
                    ensure_ascii=False
                )
            }
        ]
    }


def main():
    print("=" * 60)
    print("WILLOVATE FINE-TUNING DATA PREPARATION")
    print("=" * 60)

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    required = {
        "instruction",
        "expected_intent",
        "expected_entities",
        "expected_workflow",
        "missing_fields",
        "risk_level"
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )

    if len(df) != 400:
        raise ValueError(
            f"Expected 400 rows, found {len(df)}"
        )

    print(f"Total examples: {len(df)}")

    random.seed(SEED)

    indices = list(range(len(df)))
    random.shuffle(indices)

    train_indices = indices[:TRAIN_SIZE]
    eval_indices = indices[
        TRAIN_SIZE:TRAIN_SIZE + EVAL_SIZE
    ]

    train_df = df.iloc[train_indices]
    eval_df = df.iloc[eval_indices]

    train_data = [
        make_example(row)
        for _, row in train_df.iterrows()
    ]

    eval_data = [
        make_example(row)
        for _, row in eval_df.iterrows()
    ]

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    train_path = OUTPUT_DIR / "train.jsonl"
    eval_path = OUTPUT_DIR / "eval.jsonl"

    with open(
        train_path,
        "w",
        encoding="utf-8"
    ) as f:
        for item in train_data:
            f.write(
                json.dumps(
                    item,
                    ensure_ascii=False
                ) + "\n"
            )

    with open(
        eval_path,
        "w",
        encoding="utf-8"
    ) as f:
        for item in eval_data:
            f.write(
                json.dumps(
                    item,
                    ensure_ascii=False
                ) + "\n"
            )

    print()
    print("Dataset prepared successfully.")
    print(f"Training examples:   {len(train_data)}")
    print(f"Evaluation examples: {len(eval_data)}")
    print(f"Training file:       {train_path}")
    print(f"Evaluation file:     {eval_path}")
    print()
    print("The 80 evaluation examples are kept separate.")


if __name__ == "__main__":
    main()