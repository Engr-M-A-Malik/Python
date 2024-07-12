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

# Ask user if they want cover letters for irrelevant jobs as well
cover_both = input("Generate cover letters for irrelevant jobs as well? (yes/no): ").lower() == 'yes'

# Define and create directories based on user choice
if cover_both:
    relevant_dir = 'cover_letters_relevant'
    irrelevant_dir = 'cover_letters_irrelevant'
    os.makedirs(relevant_dir, exist_ok=True)
    os.makedirs(irrelevant_dir, exist_ok=True)
else:
    relevant_dir = 'cover_letters'
    os.makedirs(relevant_dir, exist_ok=True)

# Process each job description and generate a cover letter
directories = {'relevant_job_descriptions': relevant_dir}
if cover_both:
    directories['irrelevant_job_descriptions'] = irrelevant_dir

for directory, save_dir in directories.items():
    for filename in os.listdir(directory):
        company_name = filename.replace('.json', '')
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
            data = json.load(f)
            job_description = data['job_description']

        # Start a chat session and send a message
        chat_session = model.start_chat()
        response = chat_session.send_message(f"Based on the following job description, please create a tailored cover letter: {job_description}")
        
        # Save the generated cover letter in the corresponding directory
        cover_letter_path = os.path.join(save_dir, f"{company_name}.txt")
        with open(cover_letter_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            print(f"Saved cover letter for {company_name} in {save_dir}")