from torch import nn
from transformers import AutoModel, AutoTokenizer

class LlamaClassifier(nn.Module):
    def __init__(self, model_id, num_labels):
        super().__init__()
        self.llama = AutoModel.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

        for param in self.llama.parameters():
            param.requires_grad = False  # Optional: freeze llama

        self.classifier = nn.Linear(self.llama.config.hidden_size, num_labels)

    def forward(self, input_ids, attention_mask=None):
        outputs = self.llama(input_ids=input_ids, attention_mask=attention_mask)
        hidden_states = outputs.last_hidden_state  # (batch_size, seq_len, hidden_size)

        pooled = hidden_states.mean(dim=1)  # Mean pooling, same as bert
        logits = self.classifier(pooled)
        return logits