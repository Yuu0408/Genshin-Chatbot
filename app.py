from quart import Quart, render_template, websocket, send_from_directory
from langchain_openai import OpenAI
import boto3
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import os
import time
from datetime import datetime
import glob
from execute_task import classify_and_execute_task
from openai import OpenAI
import asyncio
from helper import labels_to_emotions
from memory_process import memory_process, retrieve_information, process_history
from setup import OPENAI_API_KEY, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


app = Quart(__name__)
app.secret_key = os.urandom(24)

# Model for text generation
client = OpenAI()

# Model for emotion detection
checkpoint = './emotion_model'
tokenizer = AutoTokenizer.from_pretrained("j-hartmann/emotion-english-distilroberta-base")
model = AutoModelForSequenceClassification.from_pretrained(checkpoint)
emotion_classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, return_all_scores=False)

# Replace the following values with your actual AWS credentials and region
polly_client = boto3.client(
    'polly',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def delete_existing_audio_files():
    files = glob.glob('audio/*.mp3')
    for f in files:
        os.remove(f)

async def emotion_classify(chunk_message):
    return emotion_classifier(chunk_message)

async def synthesize_speech(text, voice_id='Salli'):
    start = time.time()
    
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId=voice_id,
    )
    if 'AudioStream' in response:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        audio_path = f'audio/speech_{timestamp}.mp3'
        with open(audio_path, 'wb') as audio_file:
            audio_file.write(response['AudioStream'].read())
            audio_file.flush()
    end = time.time()
    print(f"audio-to-text time: {end-start} seconds")
    return audio_path

with open('data/character_description.txt', 'r') as f:
    character_description = f.read()

with open('data/user_description.txt', 'r') as f:
    user_description = f.read()

@app.route('/')
async def index():
    return await render_template('index.html')

@app.websocket('/ws')
async def ws():
    while True:
        user_input = await websocket.receive_json()
        user_input = user_input.get('message')
        # If user input is a task, classify and execute the task
        if user_input:
            asyncio.create_task(classify_and_execute_task(user_input))
        
        print(f"user input: {user_input}")

        with open('data/history.txt', 'a') as f:
            f.write(f'Me: {user_input}\n')

        with open('data/memory.txt', 'a') as f:
            f.write(f'Yuu: {user_input}\n')

        with open('data/history.txt', 'r') as f:
            history = f.read()
        
        retrieved_information = await retrieve_information()

        # Create prompt
        prompt = f"""
            You are Furina. Answer me as Furina.
            Here is the description about me:
            {user_description}
            Here is the description about you:
            {character_description}
            Here is the information you can use if you need, when you don't know things related to the current conversation:
            {retrieved_information}
            Here is the chat history:
            % CHAT HISTORY:
            {history}
            %YOUR ANSWER:
            """

        # LLM generated response with stream
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": prompt},
                {'role': 'user', 'content': user_input}
            ],
            temperature=0.7,
            stream=True
        )

        chunk_tokens = [] # List to store every token the model generated
        messages_list = [] # List to store every chunk message the model generated.

        # Delete all previous generated audio files
        delete_existing_audio_files()

        start_time = time.time()
        total_time = 0

        # Create a loop to build and process sentences from LLM generated token chunks
        count = 0
        for chunk in response:
            token = chunk.choices[0].delta.content
            if token is not None:
                # Handle unexpected generated text
                if '\n' in token:
                    token = token[0]
                # Sometimes, the generated text contains *{action}*. We have to remove it
                if "*" in token:
                    count += 1
                if count == 1:
                    continue
                elif count == 2:
                    count = 0
                    continue
                else:
                    chunk_tokens.append(token)
            
            else:
                continue

            # Build a sentence from chunk_tokens when token is the end of a sentence
            if any(punctuation in token for punctuation in {'.', '!', '?', '。', '？', '！'}):
                response_time = time.time() - start_time
                print(f"response time from start: {response_time} seconds")
                total_time += response_time

                chunk_message = ''.join(chunk_tokens)
                messages_list.append(chunk_message) # Append the sentence to messages_list
                chunk_tokens = [] # Clear the chunk_tokens for the next sentence
                
                process_start = time.time() # Start time for emotion detection, text-to-speech process
                # Emotion detection
                predictions = await emotion_classify(chunk_message)
                emotion = labels_to_emotions[predictions[0]['label']]
                print(f"Emotion: {emotion}")

                # Text-to-speech
                audio_path = await synthesize_speech(chunk_message)
                if audio_path:
                    await websocket.send_json({
                        'message': chunk_message, 
                        'emotion': emotion,
                        'audio_url': audio_path
                    })

                    # Adding this code makes the audio play immediately without waiting for all other audios to be completely generated
                    await asyncio.sleep(0.1)

                else:
                    await websocket.send_json({
                        'message': chunk_message, 
                        'emotion': emotion,
                        'error': "Failed to synthesize speech"
                    })
                    await asyncio.sleep(0.1)
                    
                process_end = time.time() # end time for emotion detection, text-to-speech process

                print(f"Audio generation and emotion detection time: {process_end - process_start} seconds")
                total_time += (process_end - process_start) # Update the total processing time for all responses
                print(f"Message: {chunk_message}")

        # Update the chat history and short term memory
        messages = ' '.join(messages_list)
        with open('data/history.txt', 'a') as f:
            f.write(f'You: {messages}\n')

        with open('data/memory.txt', 'a') as f:
            f.write(f'Furina: {messages}\n')

        print(f"Message: {messages}")
        print(f"Total time: {total_time}")
        total_time = 0
        await process_history()
        asyncio.create_task(memory_process())

@app.route('/audio/<filename>')
async def get_audio(filename):
    return await send_from_directory('audio', filename)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
