from torch import nn
from peft import LoraConfig, get_peft_model

from transformers import AutoTokenizer, AutoModel

class LlamaClassifier(nn.Module):
    def __init__(self, model_id, num_labels, lora_r=8, lora_alpha=16, lora_dropout=0.1):
        super().__init__()
        self.llama = AutoModel.from_pretrained(model_id)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

        lora_config = LoraConfig(
            r=lora_r,
            lora_alpha=lora_alpha,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  
            lora_dropout=lora_dropout,
            bias="none",
            task_type="SEQ_CLS"  # sequence classification
        )
        self.llama = get_peft_model(self.llama, lora_config)
        
        self.classifier = nn.Linear(self.llama.config.hidden_size, num_labels)

    def forward(self, input_ids, attention_mask=None):
        outputs = self.llama(input_ids=input_ids, attention_mask=attention_mask)
        hidden_states = outputs.last_hidden_state  # (batch_size, seq_len, hidden_size)
         
        pooled = hidden_states.mean(dim=1)  # Mean pooling, same as bert
        logits = self.classifier(pooled)
        return logits
