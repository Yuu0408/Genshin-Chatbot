from command import execute
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

checkpoint = "./task_model"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

tasks = {
  "LABEL_0": {
    "device": "Light",
    "task": "turn on"
  },
  "LABEL_1": {
    "device": "Light",
    "task": "turn off"
  },
  "LABEL_2": {
    "device": "DIY Fan",
    "task": "turn on"
  },
  "LABEL_3": {
    "device": "DIY Fan",
    "task": "turn off"
  },
  "LABEL_4": {
    "device": "Air Conditioner",
    "task": "turn on"
  },
  "LABEL_5": {
    "device": "Air Conditioner",
    "task": "turn off"
  }
}

async def classify_and_execute_task(inputs, classifier=classifier):
  print("input: ", inputs)
  predictions = classifier(inputs)
  prediction = predictions[0]
  label = prediction["label"]
  score = prediction["score"]
  if label == 'LABEL_6' or score < 0.8: # Don't accept label with certaincy < 0.8
    return None
  else:
    print("device: ", tasks[label]['device'])
    await execute(tasks[label]['device'], tasks[label]['task'])

