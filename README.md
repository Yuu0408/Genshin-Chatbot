# Genshin Chatbot
An advanced chatbot based on a character named Furina in the game Genshin Impact, leveraging GPT-4o-mini, speech recognition, text-to-speech, and a unique memory management system. This project demonstrates various NLP techniques and integrates task automation using the SwitchBot API.

## Features
- **Response Generation**: Utilizes OpenAI GPT-4o-mini API for generating responses.
- **Speech-to-Text**: Supports voice input.
- **Text-to-Speech**: Generates speech output using AWS Polly.
- **Sentiment Analysis**: Classifies emotions in responses.
- **Emotion Images**: Illustrates the state of the LLM with images.
- **Memory Architecture**: Manages current chat memory, short-term memory, and long-term memory for context-aware conversations.
- **Information Retrieval**: Zero-shot classification for topic detection and information retrieval.
- **Task Automation**: Classifies tasks and executes them like turning on/off devices using the SwitchBot API.

# Workflow Diagram
You can view the detailed workflow diagram of the Genshin Chatbot project by opening the following PDF:
[Workflow Diagram PDF](assets/workflow.pdf).

This diagram provides a visual overview of how components interact, including data flow and integration points with external APIs like OpenAI and SwitchBot.

# Setup
## 1. Install Dependencies:
Install the required dependencies:
```
pip install -r requirements.txt
```

## 2. Configure API Keys:
Fill in the required API keys in the `setup.py` file.

## 3. Initialize SwitchBot Devices (if using SwitchBot API features):
Run the following script to get the list of devices
```
python get_devices.py
```

## 4. Customize Chatbot and User Profiles:
- **Character Description**: Fill in `data/character_description.txt` with a detailed description of the chatbot's personality, style of interaction, and any specific traits you want the chatbot to emulate.
- **User Description**: Fill in `data/user_description.txt` with a detailed description of the user. This can include information like interests, typical phrases, and interaction preferences to make the chatbot's responses more personalized and context-aware.

# Usage
## 1. Run the Chatbot:
```
python app.py
```

## 2. Interacting with the Chatbot:
You can interact with the chatbot through text input or speech input.
The chatbot will generate responses and can also perform tasks if configured with the SwitchBot API.
