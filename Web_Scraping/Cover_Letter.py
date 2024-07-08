# generative_cover_letter.py

import os
import json
import google.generativeai as genai

# Configure the API
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=api_key)

# Generation model setup
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Directory for saving cover letters
os.makedirs('cover_letters', exist_ok=True)

# Read each job description and generate a cover letter
for filename in os.listdir('job_descriptions'):
    company_name = filename.replace('.json', '')
    with open(os.path.join('job_descriptions', filename), 'r', encoding='utf-8') as f:
        data = json.load(f)
        job_description = data['job_description']

    # Start a chat session and send a message
    chat_session = model.start_chat()
    response = chat_session.send_message(f"Based on the following job description, please create a tailored cover letter: {job_description}")
    
    # Save the generated cover letter
    cover_letter_path = os.path.join('cover_letters', f"{company_name}.txt")
    with open(cover_letter_path, 'w', encoding='utf-8') as f:
        f.write(response.text)
        print(f"Saved cover letter for {company_name}")
