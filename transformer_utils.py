from torch.utils.data import Dataset, DataLoader
import torch
import math

class TransformerNewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = int(self.labels[idx])
        encodings = self.tokenizer(
            text,
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors="pt"
        )
        return {
            "input_ids": encodings["input_ids"].squeeze(0),
            "attention_mask": encodings["attention_mask"].squeeze(0)
        }, torch.tensor(label)

    def embed_all(self):
        encodings = self.tokenizer(
            self.texts.to_list(),
            max_length=self.max_len,
            padding='max_length',
            truncation=True,
            return_tensors="pt"
        )
        return encodings

def cosine_with_warmup_lr_lambda(current_step: int, num_warmup_steps: int, num_cyles: float, last_epoch: int = -1) -> float:
    """cosine lambda function for learning rate schedule"""
    if current_step < num_warmup_steps:
        return current_step / max(1, num_warmup_steps)

    progress = (current_step - num_warmup_steps) / max(
        1, num_training_steps - num_warmup_steps
    )

    cosine_lr_multiple = 0.5 * (
        1.0 + math.cos(math.pi * num_cycles * 2.0 * progress)
    )
    return max(0.0, cosine_lr_multiple)