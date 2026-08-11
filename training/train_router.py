from __future__ import annotations

import json
import random
from pathlib import Path

import torch
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_NAME = "prajjwal1/bert-tiny"
LABELS = ["urgent_handoff", "scheduling", "knowledge", "general_handoff"]
LABEL_TO_ID = {label: index for index, label in enumerate(LABELS)}


class RouterDataset(Dataset):
    def __init__(self, rows: list[dict[str, str]], tokenizer: object):
        self.rows = rows
        self.tokenizer = tokenizer

    def __len__(self) -> int:
        return len(self.rows)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        row = self.rows[index]
        encoded = self.tokenizer(
            row["text"],
            truncation=True,
            padding="max_length",
            max_length=48,
            return_tensors="pt",
        )
        return {
            "input_ids": encoded["input_ids"].squeeze(0),
            "attention_mask": encoded["attention_mask"].squeeze(0),
            "labels": torch.tensor(LABEL_TO_ID[row["label"]], dtype=torch.long),
        }


def read_rows(path: Path) -> list[dict[str, str]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def accuracy(model: object, loader: DataLoader) -> float:
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for batch in loader:
            logits = model(
                input_ids=batch["input_ids"],
                attention_mask=batch["attention_mask"],
            ).logits
            predictions = logits.argmax(dim=-1)
            correct += int((predictions == batch["labels"]).sum())
            total += len(predictions)
    return round(correct / total, 4)


def main() -> None:
    torch.manual_seed(42)
    random.seed(42)
    rows = read_rows(PROJECT_ROOT / "data" / "router_train.jsonl")
    random.shuffle(rows)
    validation_size = max(8, len(rows) // 4)
    validation_rows = rows[:validation_size]
    train_rows = rows[validation_size:]

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABELS),
        id2label={index: label for index, label in enumerate(LABELS)},
        label2id=LABEL_TO_ID,
    )
    train_loader = DataLoader(RouterDataset(train_rows, tokenizer), batch_size=8, shuffle=True)
    validation_loader = DataLoader(RouterDataset(validation_rows, tokenizer), batch_size=8)
    optimizer = AdamW(model.parameters(), lr=5e-5)

    model.train()
    for _ in range(8):
        for batch in train_loader:
            optimizer.zero_grad()
            loss = model(**batch).loss
            loss.backward()
            optimizer.step()

    validation_accuracy = accuracy(model, validation_loader)
    output_dir = PROJECT_ROOT / "training" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    metrics = {
        "model": MODEL_NAME,
        "task": "four-class service-agent intent routing",
        "train_examples": len(train_rows),
        "validation_examples": len(validation_rows),
        "epochs": 8,
        "seed": 42,
        "validation_accuracy": validation_accuracy,
        "limitations": "Synthetic English examples; not a production safety benchmark.",
    }
    metrics_path = PROJECT_ROOT / "artifacts" / "router_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

