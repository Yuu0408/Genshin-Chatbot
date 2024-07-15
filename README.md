# Genshin Chat Bot
An advanced chatbot leveraging GPT-3.5, speech recognition, text-to-speech, and a unique memory management system. This project demonstrates various NLP techniques and integrates task automation using the SwitchBot API.

# Features
Response Generation: Utilizes GPT-3.5 API for generating responses.
Speech-to-Text: Supports voice input.
Text-to-Speech: Generates speech output using AWS Polly.
Emotion Images: Illustrates the state of the LLM with images.
Memory Architecture: Manages current chat memory, short-term memory, and long-term memory for context-aware conversations.
Information Retrieval: Zero-shot classification for topic detection and information retrieval.
Task Automation: Classifies tasks and executes them like turning on/off devices using the SwitchBot API.
Emotion Detection: Classifies emotions in responses.

# Setup
## 1. Configure API Keys:
Fill in the required API keys in the `setup.py` file.
## 2. Initialize SwitchBot Devices (if using SwitchBot API features):
Run the following script to get the list of devices
```
python get_devices.py
```

# Usage
## 1. Run the Chatbot:
```
python app.py
```

## 2. Interacting with the Chatbot:
You can interact with the chatbot through text input or speech input.
The chatbot will generate responses and can also perform tasks if configured with the SwitchBot API.
