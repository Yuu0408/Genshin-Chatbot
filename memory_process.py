from transformers import pipeline
from openai import OpenAI
import os
import asyncio
from datetime import datetime
from setup import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

labels = ["relationships", "health", "education", "technology", "career", "finance", "entertainment", "lifestyle", "sports", "politics"]
zeroshot_classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")

async def memory_process(labels=labels, zeroshot_classifier=zeroshot_classifier):
  def blocking_memory_process():
    with open('data/memory.txt', 'r') as f:
      memories = f.readlines()

    if len(memories) >= 10:
      with open('data/memory.txt', 'w') as f:
        f.write('')

      clean_lines = [line.strip() for line in memories]
      content = '\n'.join(clean_lines)

      client = OpenAI()
      response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
          {"role": "system", "content": """summarize this conversation as Furina, like what in the conversation Furina would remember (just write the summary, don't write any other things). Summerize the conversation as Furina, which mean you should summerize as you are Furina, and tell the story with 'I':
          % THE CONVERSATION:"""},
          {"role": "user", "content": content}
        ],
        temperature=0,
      )

      timestamp = datetime.now().strftime("%Y/%m/%d | %H:%M")
      summary = timestamp + ': ' + response.choices[0].message.content + '\n'
      print("summary: ", summary)

      topics = zeroshot_classifier(summary, candidate_labels=labels)
      topic= topics['labels'][0]
      print("topic: ", topic)

      with open(f"data/long_term_memory/{topic}.txt", 'a') as f:
        f.write(summary)

  await asyncio.to_thread(blocking_memory_process)

async def retrieve_information(labels=labels, zeroshot_classifier=zeroshot_classifier):
  inputs = []
  with open('data/history.txt', 'r') as file:
    lines = file.readlines()
  for i in range(1, len(lines)+1):
    if i == 4:
      break
    inputs.insert(0, lines[-i])
  
  input = ''.join(inputs)
  print("content to compare: ", input)

  topics = zeroshot_classifier(input, candidate_labels=labels)
  topic1, topic2 = topics['labels'][0], topics['labels'][1]
  print("Top related topics: ", topic1, ", ", topic2)

  with open(f"data/long_term_memory/{topic1}.txt", 'r') as f:
    content1 = f.read()

  with open(f"data/long_term_memory/{topic2}.txt", 'r') as f:
    content2 = f.read()
  
  retrieved_information = content1 + content2
  print("Retrieved_information: ", retrieved_information)

  return retrieved_information

# asyncio.run(retrieve_information(labels, zeroshot_classifier))

async def process_history():
  with open('data/history.txt', 'r') as f:
    lines = f.readlines()
  
  while len(lines) > 20:
    lines.pop(0)

  new_history = ''.join(lines)
  with open('data/history.txt', 'w') as f:
    f.write(new_history)
  