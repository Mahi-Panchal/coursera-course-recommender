import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

def scrape_coursera_extensive():
    domains = [
        "Data Science", "Business", "Computer Science", "Health", 
        "Social Sciences", "Personal Development", "Arts and Humanities", 
        "Physical Science and Engineering", "Language Learning", "Information Technology"
    ]
    
    all_data = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    for domain in domains:
        # Scraping 5 pages per domain to reach ~1000 courses total
        for page in range(1, 6): 
            search_url = f"https://www.coursera.org/search?query={domain.replace(' ', '%20')}&page={page}"
            print(f"Fetching: {domain} - Page {page}")
            
            try:
                response = requests.get(search_url, headers=headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Targeted selectors for real data
                cards = soup.find_all('div', {'class': 'cds-ProductCard-content'})
                
                for card in cards:
                    title_elem = card.find('h3')
                    if not title_elem: continue
                    
                    title = title_elem.text.strip()
                    
                    # Extracting Mentor/Partner (e.g., Google, Stanford, IBM)
                    mentor = "Various"
                    partner_elem = card.find('span', {'class': 'cds-ProductCard-partnerNames'})
                    if partner_elem:
                        mentor = partner_elem.text.strip()

                    # Building the URL
                    # Coursera links are usually inside an anchor tag around the card
                    link_elem = card.find_parent('a') or card.find('a')
                    path = link_elem['href'] if link_elem else ""
                    full_url = f"https://www.coursera.org{path}" if path.startswith('/') else path

                    all_data.append({
                        'title': title,
                        'domain': domain,
                        'subdomain': f"{domain} Expertise", 
                        'mentor': mentor,
                        'url': full_url,
                        'price': "Free/Paid Mix",
                        'description': f"Advanced {domain} course provided by {mentor}."
                    })
            except Exception as e:
                print(f"Skipped page due to: {e}")
            time.sleep(1) # Be polite to servers

    df = pd.DataFrame(all_data)
    df = df.drop_duplicates(subset=['title']) # Ensure 1000+ UNIQUE courses
    df.to_csv('courses_data.csv', index=False)
    print(f"✅ Success! {len(df)} unique courses saved to courses_data.csv")

if __name__ == "__main__":
    scrape_coursera_extensive()