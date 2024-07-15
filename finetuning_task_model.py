from transformers import AutoTokenizer, AutoModelForSequenceClassification, DataCollatorWithPadding, get_scheduler, AdamW
from datasets import Dataset
import pandas as pd
from finetuning_data import val_data, train_data
from torch.utils.data import DataLoader


# Convert to pandas DataFrame
train_df = pd.DataFrame(train_data)
val_df = pd.DataFrame(val_data)

# Convert to Dataset object
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

# Map labels to integers
label_to_id = {
    "turn_on_light": 0,
    "turn_off_light": 1,
    "turn_on_fan": 2,
    "turn_off_fan": 3,
    "turn_on_air_conditional": 4,
    "turn_off_air_conditional": 5,
    "others": 6
}

# Apply label mapping
train_dataset = train_dataset.map(lambda examples: {'labels': label_to_id[examples['label']]})
val_dataset = val_dataset.map(lambda examples: {'labels': label_to_id[examples['label']]})

# Define tokenizer and model
checkpoint = "./task_model"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=len(label_to_id))

# Tokenize the data
def tokenize_function(examples):
    return tokenizer(examples['text'], truncation=True)

tokenized_train_dataset = train_dataset.map(tokenize_function, batched=True)
tokenized_val_dataset = val_dataset.map(tokenize_function, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

tokenized_train_dataset = tokenized_train_dataset.remove_columns(["text", "label"])
tokenized_train_dataset.set_format("torch")
tokenized_val_dataset = tokenized_val_dataset.remove_columns(["text", "label"])
tokenized_val_dataset.set_format("torch")

train_dataloader = DataLoader(
    tokenized_train_dataset, shuffle=True, batch_size=8, collate_fn=data_collator
)
eval_dataloader = DataLoader(
    tokenized_val_dataset, batch_size=8, collate_fn=data_collator
)
for batch in train_dataloader:
    break
print({k: v.shape for k, v in batch.items()})

outputs = model(**batch)
print(outputs.loss, outputs.logits.shape)

optimizer = AdamW(model.parameters(), lr=5e-5)

num_epochs = 20
num_training_steps = num_epochs * len(train_dataloader)
lr_scheduler = get_scheduler(
    "linear",
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps,
)
print(num_training_steps)

import torch

device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model.to(device)
print(device)

from tqdm.auto import tqdm

progress_bar = tqdm(range(num_training_steps))

model.train()
for epoch in range(num_epochs):
    for batch in train_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()

        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        progress_bar.update(1)

import evaluate

metric = evaluate.load('f1', config_name='multiclass')
model.eval()
progress_bar = tqdm(eval_dataloader, desc='Evaluating')
for batch in progress_bar:
    batch = {k: v.to(device) for k, v in batch.items()}
    with torch.no_grad():
        outputs = model(**batch)
    
    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1)
    metric.add_batch(predictions=predictions.cpu(), references=batch["labels"].cpu())

results = metric.compute(average='macro')  # You can choose 'micro', 'macro', or 'weighted' depending on your needs
print(results)

model.save_pretrained('./task_model')