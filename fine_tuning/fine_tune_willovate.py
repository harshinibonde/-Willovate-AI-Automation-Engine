import ast
import json
import random
from pathlib import Path

import pandas as pd
import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoTokenizer
from trl import SFTConfig, SFTTrainer

MODEL_NAME = "openai/gpt-oss-20b"
ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "src" / "willovate" / "dataset" / "willovate_evaluation_dataset.csv"
OUTPUT_DIR = ROOT / "fine_tuning" / "outputs"
DATA_DIR = ROOT / "fine_tuning" / "data"
TRAIN_FILE = DATA_DIR / "train.jsonl"
EVAL_FILE = DATA_DIR / "eval.jsonl"

SEED = 42
TRAIN_SIZE = 320
EVAL_SIZE = 80
NUM_EPOCHS = 2
LEARNING_RATE = 1e-4
MAX_LENGTH = 2048

SYSTEM_PROMPT = """You are Willovate, an AI automation engine.
Your job is to understand a user's natural-language automation request
and convert it into structured automation information.
Return ONLY valid JSON using exactly this structure:
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
Supported workflow actions:
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
- Never invent entity values.
- Extract entities only from the user instruction.
- If required information is missing, list it in missing_fields.
- Do not invent workflow actions.
- Use only supported actions.
- Preserve the requested order.
- Use only information provided by the user.
- Risky actions must be classified appropriately.
- Return valid JSON only.
- Do not include markdown.
- Do not include explanations outside JSON.
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

def normalize_entities(value):
    value = parse_value(value)
    if isinstance(value, dict):
        return value
    return {}

def normalize_workflow(value):
    value = parse_value(value)
    if isinstance(value, list):
        return value
    return []

def normalize_missing_fields(value):
    value = parse_value(value)
    if isinstance(value, list):
        return value
    return []

def create_answer(row):
    return {
        "intent": str(row["expected_intent"]).strip(),
        "entities": normalize_entities(row["expected_entities"]),
        "missing_fields": normalize_missing_fields(row["missing_fields"]),
        "risk_level": str(row["risk_level"]).strip(),
        "workflow": normalize_workflow(row["expected_workflow"])
    }

def create_training_example(row):
    answer = create_answer(row)
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": str(row["instruction"]).strip()},
            {
                "role": "assistant",
                "content": json.dumps(answer, ensure_ascii=False)
            }
        ]
    }

def write_jsonl(path, examples):
    with open(path, "w", encoding="utf-8") as file:
        for example in examples:
            file.write(json.dumps(example, ensure_ascii=False) + "\n")

def prepare_dataset():
    print("=" * 60)
    print("WILLOVATE FINE-TUNING DATASET PREPARATION")
    print("=" * 60)
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found:\n{DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    required_columns = {
        "instruction",
        "expected_intent",
        "expected_entities",
        "expected_workflow",
        "missing_fields",
        "risk_level"
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            "Dataset is missing columns: " + str(sorted(missing_columns))
        )
    print(f"Dataset: {DATASET_PATH}")
    print(f"Total examples: {len(df)}")
    if len(df) != 400:
        raise ValueError(f"Expected 400 examples, found {len(df)}")
    random.seed(SEED)
    indices = list(range(len(df)))
    random.shuffle(indices)
    train_indices = indices[:TRAIN_SIZE]
    eval_indices = indices[TRAIN_SIZE:TRAIN_SIZE + EVAL_SIZE]
    train_df = df.iloc[train_indices].reset_index(drop=True)
    eval_df = df.iloc[eval_indices].reset_index(drop=True)
    train_examples = [
        create_training_example(row)
        for _, row in train_df.iterrows()
    ]
    eval_examples = [
        create_training_example(row)
        for _, row in eval_df.iterrows()
    ]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl(TRAIN_FILE, train_examples)
    write_jsonl(EVAL_FILE, eval_examples)
    print(f"Training examples: {len(train_examples)}")
    print(f"Evaluation examples: {len(eval_examples)}")
    print(f"Training file: {TRAIN_FILE}")
    print(f"Evaluation file: {EVAL_FILE}")

def load_datasets():
    print("=" * 60)
    print("LOADING DATASETS")
    print("=" * 60)
    train_df = pd.read_json(TRAIN_FILE, lines=True)
    eval_df = pd.read_json(EVAL_FILE, lines=True)
    train_dataset = Dataset.from_pandas(train_df, preserve_index=False)
    eval_dataset = Dataset.from_pandas(eval_df, preserve_index=False)
    print(f"Train dataset: {len(train_dataset)}")
    print(f"Eval dataset: {len(eval_dataset)}")
    return train_dataset, eval_dataset

def check_hardware():
    print("=" * 60)
    print("HARDWARE CHECK")
    print("=" * 60)
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = (
            torch.cuda.get_device_properties(0).total_memory
            / (1024 ** 3)
        )
        print(f"GPU: {gpu_name}")
        print(f"VRAM: {gpu_memory:.2f} GB")
    else:
        print("WARNING: CUDA is not available.")
        print("gpt-oss-20b fine-tuning requires a suitable accelerator.")
        raise RuntimeError(
            "CUDA GPU required for this training configuration."
        )

def train(train_dataset, eval_dataset):
    print("=" * 60)
    print("STARTING WILLOVATE FINE-TUNING")
    print("=" * 60)
    print(f"Base model: {MODEL_NAME}")
    print(f"Epochs: {NUM_EPOCHS}")
    print(f"Learning rate: {LEARNING_RATE}")
    print("Method: LoRA + Supervised Fine-Tuning")
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj"
        ]
    )
    use_bf16 = (
        torch.cuda.is_available()
        and torch.cuda.is_bf16_supported()
    )
    dtype = torch.bfloat16 if use_bf16 else torch.float16
    training_args = SFTConfig(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=8,
        gradient_checkpointing=True,
        logging_steps=5,
        save_strategy="epoch",
        eval_strategy="epoch",
        load_best_model_at_end=False,
        report_to="none",
        max_length=MAX_LENGTH,
        packing=False,
        model_init_kwargs={
            "torch_dtype": dtype,
            "trust_remote_code": True
        }
    )
    trainer = SFTTrainer(
        model=MODEL_NAME,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
        peft_config=lora_config
    )
    print("Training...")
    trainer.train()
    print("Training complete.")
    final_output = OUTPUT_DIR / "willovate-gpt-oss-20b-lora"
    trainer.save_model(str(final_output))
    tokenizer.save_pretrained(str(final_output))
    print("=" * 60)
    print("MODEL SAVED")
    print("=" * 60)
    print(final_output)
    return trainer

def evaluate(trainer):
    print("=" * 60)
    print("EVALUATING FINE-TUNED MODEL")
    print("=" * 60)
    metrics = trainer.evaluate()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: {value:.6f}")
        else:
            print(f"{key}: {value}")
    metrics_path = OUTPUT_DIR / "fine_tuning_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)
    print(f"Metrics saved to: {metrics_path}")

def main():
    print("=" * 60)
    print("WILLOVATE MODEL FINE-TUNING")
    print("=" * 60)
    print(f"Base model: {MODEL_NAME}")
    print(f"Dataset: {DATASET_PATH}")
    prepare_dataset()
    check_hardware()
    train_dataset, eval_dataset = load_datasets()
    trainer = train(train_dataset, eval_dataset)
    evaluate(trainer)
    print("=" * 60)
    print("WILLOVATE FINE-TUNING COMPLETE")
    print("=" * 60)
    print("320 development examples were used for training.")
    print("80 evaluation examples were kept separate.")
    print("Next: compare base vs fine-tuned model on the same 80 examples.")

if __name__ == "__main__":
    main()