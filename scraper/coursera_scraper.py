import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

# ==============================
# DOMAIN SEARCH QUERIES
# ==============================
DOMAINS = [
    "Artificial Intelligence",
    "Data Science",
    "Web Development",
    "Cloud Computing",
    "Cybersecurity",
    "Mobile Development",
    "Blockchain",
    "UI UX",
    "DevOps",
    "Programming"
]


# ==============================
# SCRAPE COURSE DETAIL PAGE
# ==============================
def scrape_course_details(course_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(course_url, headers=headers, timeout=10)

        if response.status_code != 200:
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(" ", strip=True)

        # --------------------------
        # DESCRIPTION
        # --------------------------
        description = text[:500]

        # --------------------------
        # LEVEL
        # --------------------------
        level = ""
        for lv in ["Beginner", "Intermediate", "Advanced", "Mixed"]:
            if lv.lower() in text.lower():
                level = lv
                break

        # --------------------------
        # BETTER MENTOR / PROVIDER
        # --------------------------
        mentor = "Not Available"

        mentor_patterns = [
            r"Taught by\s+([A-Za-z0-9&.\-\s]+)",
            r"Instructor[s]?:\s*([A-Za-z0-9&.\-\s]+)",
            r"Created by\s+([A-Za-z0-9&.\-\s]+)",
            r"Offered by\s+([A-Za-z0-9&.\-\s]+)"
        ]

        for pattern in mentor_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                mentor = match.group(1).strip()

                # clean long captures
                mentor = mentor.split("Enroll")[0]
                mentor = mentor.split("Learn")[0]
                mentor = mentor.split("Skills")[0]

                # keep short clean provider name
                mentor = " ".join(mentor.split()[:4])
                break

        return {
            "description": description,
            "skills": "",
            "level": level,
            "mentor": mentor,
            "rating": "",
            "duration": "",
            "price": "Paid"
        }

    except Exception as e:
        print(f"Error in detail scraping: {e}")
        return {}


# ==============================
# SCRAPE DOMAIN SEARCH PAGE
# ==============================
def scrape_domain_courses(domain, max_courses=20):
    print(f"Scraping domain: {domain}")

    search_url = f"https://www.coursera.org/search?query={domain.replace(' ', '%20')}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        print(f"Failed for {domain}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    courses = []
    links = soup.find_all("a", href=True)
    seen_links = set()

    for link in links:
        href = link["href"]

        if "/learn/" in href:
            if href.startswith("http"):
                full_url = href
            else:
                full_url = "https://www.coursera.org" + href

            if full_url in seen_links:
                continue

            seen_links.add(full_url)

            title = link.get_text(strip=True)
            if not title:
                title = "Unknown Course"

            details = scrape_course_details(full_url)

            course_data = {
                "course_name": title,
                "domain": domain,
                "subdomain": "",
                "mentor": details.get("mentor", "Not Available"),
                "duration": details.get("duration", ""),
                "price": details.get("price", "Paid"),
                "rating": details.get("rating", ""),
                "level": details.get("level", ""),
                "skills": details.get("skills", ""),
                "description": details.get("description", ""),
                "course_url": full_url
            }

            courses.append(course_data)

            if len(courses) >= max_courses:
                break

    time.sleep(random.uniform(1, 2))
    return courses


# ==============================
# MAIN SCRAPER
# ==============================
def run_scraper():
    all_courses = []

    for domain in DOMAINS:
        domain_courses = scrape_domain_courses(domain, max_courses=20)
        all_courses.extend(domain_courses)

    df = pd.DataFrame(all_courses)

    df.to_csv("data/coursera_courses.csv", index=False, encoding="utf-8")
    print("CSV saved successfully!")


if __name__ == "__main__":
    run_scraper()
