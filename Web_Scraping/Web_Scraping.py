from bs4 import BeautifulSoup
import requests
import csv
import os
import json

def clean_filename(filename):
    return "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()

# Create directory for job descriptions if it doesn't already exist
os.makedirs('job_descriptions', exist_ok=True)

# User inputs for dynamic URL creation
a = input("Enter the Job Title: ").replace(" ", "%2B")
b = input("Enter Country: ").replace(" ", "%2B")

# Construct the URL and fetch the initial content
url = f'https://www.linkedin.com/jobs/search?keywords={a}&location={b}'
initial_content = requests.get(url).text
initial_soup = BeautifulSoup(initial_content, 'lxml')

# Find all job links
links = initial_soup.find_all('a', class_='base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]')

# CSV to store job data
csv_filename = 'all_jobs.csv'
with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Job Title', 'Company', 'Location', 'URL'])

    for link in links:
        job_url = link['href']
        job_content = requests.get(job_url).text
        job_soup = BeautifulSoup(job_content, 'lxml')

        job_title_element = job_soup.find('h1', class_='top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title')
        if job_title_element:
            Job_Title = job_title_element.text.strip()
        else:
            print(f"Job title not found for URL: {job_url}")
            continue  # Skip this iteration and move to the next link

        Company = job_soup.find('a', class_='topcard__org-name-link topcard__flavor--black-link').text.strip().replace(" ", "")
        Location = job_soup.find('span', class_='topcard__flavor topcard__flavor--bullet').text.strip().replace(" ", "")
        description_section = job_soup.find('div', class_='description__text')

        if description_section:
            job_description = description_section.get_text(separator='\n', strip=True)
            job_description = job_description.replace('Show more', '').replace('Show less', '')

            # Write job data to CSV
            writer.writerow([Job_Title, Company, Location, job_url])

            # Save job description to JSON for inter-script communication
            description_path = os.path.join('job_descriptions', f"{clean_filename(Company)}.json")
            with open(description_path, 'w', encoding='utf-8') as f:
                json.dump({'job_description': job_description}, f)

            print(f"Saved data and description for {Company}")

        else:
            print(f"No job description found for URL: {job_url}\n\n")
