import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

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


# =========================
# DURATION CONVERTER
# =========================
def convert_duration_to_months(text):
    text = text.lower()

    week_match = re.search(r"(\d+)\s*week", text)
    hour_match = re.search(r"(\d+)\s*hour", text)
    month_match = re.search(r"(\d+)\s*month", text)

    if month_match:
        return f"{month_match.group(1)} months"

    if week_match:
        weeks = int(week_match.group(1))
        months = max(1, round(weeks / 4))
        return f"{months} months"

    if hour_match:
        hours = int(hour_match.group(1))
        months = max(1, round(hours / 40))
        return f"{months} months"

    return "1 month"


# =========================
# SUBDOMAIN GENERATOR
# =========================
def infer_subdomain(title, description):
    text = f"{title} {description}".lower()

    keywords = {
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning", "neural"],
        "NLP": ["nlp", "natural language"],
        "Frontend": ["react", "frontend", "html", "css"],
        "Backend": ["django", "flask", "node", "backend"],
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes"],
        "Blockchain Development": ["solidity", "ethereum", "smart contract"]
    }

    for sub, words in keywords.items():
        if any(word in text for word in words):
            return sub

    return "General"


# =========================
# SKILLS EXTRACTOR
# =========================
def extract_skills(text):
    common_skills = [
        "Python", "Machine Learning", "Deep Learning",
        "SQL", "React", "JavaScript", "AWS",
        "Docker", "Kubernetes", "Cybersecurity",
        "TensorFlow", "Data Analysis"
    ]

    found = [skill for skill in common_skills if skill.lower() in text.lower()]
    return ", ".join(found)


# =========================
# COURSE DETAIL SCRAPER
# =========================
def scrape_course_details(course_url):
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(course_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return {}

        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text("\n", strip=True)

        description = text[:800]

        # level
        level = "All Levels"
        for lv in ["Beginner", "Intermediate", "Advanced", "Mixed"]:
            if lv.lower() in text.lower():
                level = lv
                break

        # mentor
        mentor = "Unknown"
        mentor_patterns = [
            r"Instructor[:\s]+([A-Z][A-Za-z.\-\s]+)",
            r"Taught by[:\s]+([A-Z][A-Za-z.\-\s]+)",
            r"Created by[:\s]+([A-Z][A-Za-z.\-\s]+)"
        ]

        for pattern in mentor_patterns:
            match = re.search(pattern, text)
            if match:
                mentor = match.group(1).strip()
                break

        mentor = " ".join(mentor.split()[:3])

        # rating
        rating = ""
        rating_match = re.search(r"(\d\.\d)\s*\(", text)
        if rating_match:
            rating = rating_match.group(1)

        # duration
        duration = convert_duration_to_months(text)

        # skills
        skills = extract_skills(text)

        return {
            "description": description,
            "skills": skills,
            "level": level,
            "mentor": mentor,
            "rating": rating,
            "duration": duration,
            "price": "Paid"
        }

    except Exception as e:
        print(f"Error: {e}")
        return {}


# =========================
# DOMAIN SCRAPER
# =========================
def scrape_domain_courses(domain, max_courses=20):
    print(f"Scraping {domain}")

    search_url = f"https://www.coursera.org/search?query={domain.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    courses = []
    seen = set()

    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "/learn/" not in href:
            continue

        full_url = href if href.startswith("http") else "https://www.coursera.org" + href

        if full_url in seen:
            continue
        seen.add(full_url)

        title = link.get_text(strip=True)
        if not title:
            continue

        details = scrape_course_details(full_url)

        subdomain = infer_subdomain(title, details.get("description", ""))

        courses.append({
            "course_name": title,
            "domain": domain,
            "subdomain": subdomain,
            "mentor": details.get("mentor", "Unknown"),
            "duration": details.get("duration", "1 month"),
            "price": details.get("price", "Paid"),
            "rating": details.get("rating", ""),
            "level": details.get("level", ""),
            "skills": details.get("skills", ""),
            "description": details.get("description", ""),
            "course_url": full_url
        })

        if len(courses) >= max_courses:
            break

    time.sleep(random.uniform(1, 2))
    return courses


def run_scraper():
    all_courses = []

    for domain in DOMAINS:
        all_courses.extend(scrape_domain_courses(domain))

    df = pd.DataFrame(all_courses)
    df.drop_duplicates(subset=["course_url"], inplace=True)

    df.to_csv("data/coursera_courses.csv", index=False, encoding="utf-8")
    print("CSV saved successfully!")
