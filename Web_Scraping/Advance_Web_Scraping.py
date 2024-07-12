from bs4 import BeautifulSoup
import requests
import csv
import os
import json

def clean_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()

# Create directories for job descriptions if they don't already exist
os.makedirs('relevant_job_descriptions', exist_ok=True)
os.makedirs('irrelevant_job_descriptions', exist_ok=True)

# User inputs for dynamic URL creation
job_title_query = input("Enter the Job Title: ")
country_query = input("Enter Country: ").replace(" ", "%2B")
encoded_job_title = job_title_query.replace(" ", "%2B")

# Construct the URL and fetch the initial content
url = f'https://www.linkedin.com/jobs/search?keywords={encoded_job_title}&location={country_query}'
initial_content = requests.get(url).text
initial_soup = BeautifulSoup(initial_content, 'lxml')

# Find all job links
links = initial_soup.find_all('a', class_='base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]')

# CSV to store job data
relevant_csv = 'relevant_jobs.csv'
irrelevant_csv = 'irrelevant_jobs.csv'

# Open CSV files for writing
with open(relevant_csv, mode='w', newline='', encoding='utf-8') as relevant_file, \
     open(irrelevant_csv, mode='w', newline='', encoding='utf-8') as irrelevant_file:
    relevant_writer = csv.writer(relevant_file)
    irrelevant_writer = csv.writer(irrelevant_file)
    relevant_writer.writerow(['Job Title', 'Company', 'Location', 'URL'])
    irrelevant_writer.writerow(['Job Title', 'Company', 'Location', 'URL'])

    for link in links:
        job_url = link['href']
        job_content = requests.get(job_url).text
        job_soup = BeautifulSoup(job_content, 'lxml')

        job_title_element = job_soup.find('h1', class_='top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title')
        if job_title_element:
            job_title = job_title_element.text.strip()
        else:
            print(f"Job title not found for URL: {job_url}")
            continue  # Skip this iteration and move to the next link

        company = job_soup.find('a', class_='topcard__org-name-link topcard__flavor--black-link').text.strip()
        location = job_soup.find('span', class_='topcard__flavor topcard__flavor--bullet').text.strip()
        description_section = job_soup.find('div', class_='description__text')

        if description_section:
            job_description = description_section.get_text(separator='\n', strip=True)
            job_description = job_description.replace('Show more', '').replace('Show less', '')

            # Determine relevance using a more careful check
            normalized_job_title_query = job_title_query.lower().split()
            is_relevant = all(word.lower() in job_title.lower() for word in normalized_job_title_query)

            description_directory = 'relevant_job_descriptions' if is_relevant else 'irrelevant_job_descriptions'
            csv_writer = relevant_writer if is_relevant else irrelevant_writer

            # Write job data to relevant or irrelevant CSV
            csv_writer.writerow([job_title, company, location, job_url])

            # Save job description in the correct directory
            description_filename = f"{clean_filename(company)}_{clean_filename(job_title)}.json"
            description_path = os.path.join(description_directory, description_filename)
            with open(description_path, 'w', encoding='utf-8') as f:
                json.dump({'job_description': job_description}, f)

            print(f"Saved data and description for {company} in {description_directory}")

        else:
            print(f"No job description found for URL: {job_url}\n\n")
