# python file to search for new papers on epilepsy neurotech
import os
import smtplib
import datetime
import requests
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import openai

# Expanded search parameters
SEARCH_QUERY = (
    "(epilepsy OR seizure EEG OR MRI OR MEG OR PET OR AI OR Machine learning)  site:scholar.google.com "
)
SEARCH_ENGINE_URL = "https://www.bing.com/search?q="

# Extract credentials from environment variables
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
RECEIVER_EMAIL = "benbrinkmann@gmail.com"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI key
openai.api_key = OPENAI_API_KEY

def search_courses():
    """Search expanded sources and collect course data."""
    print("🔍 Searching for new papers on epilepsy neurotechnology...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.133 Safari/537.36"
    }

    try:
        response = requests.get(SEARCH_ENGINE_URL + SEARCH_QUERY, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Unable to fetch search results - {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    courses = []

    for result in soup.find_all("li", class_="b_algo")[:30]:
        try:
            title = result.find("h2").text if result.find("h2") else "No title found"
            link = result.find("a")["href"] if result.find("a") else "No link"
            description = result.find("p").text if result.find("p") else "No description available"
        except AttributeError:
            continue  # Skip malformed results
        
        courses.append({
            "title": title,
            "link": link,
            "description": description,
            "cost": "Varies (Check link)",
            "prerequisites": "Check link for details"
        })
    
    print(f"✅ Collected {len(courses)} raw opportunities.")
    return courses

def summarize_and_rank(courses):
    """Use OpenAI to summarize and rank the best opportunities."""
    print("🤖 Summarizing and ranking opportunities with ChatGPT...")
    if not OPENAI_API_KEY:
        print("❌ ERROR: Missing OpenAI API Key!")
        return fallback_summary(courses)

    prompt = (
        "You are an expert career advisor. Analyze and rank the following AI leadership and medical imaging course opportunities "
        "for career advancement. Summarize the top 5, include title, brief summary, cost, format, and why it is valuable.\n\n"
    )

    for course in courses:
        prompt += f"Title: {course['title']}\nLink: {course['link']}\nDescription: {course['description']}\n\n"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You summarize AI training opportunities."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        summary = response.choices[0].message['content']
        print("✅ Summarization complete.")
        return summary
    except Exception as e:
        print(f"❌ ERROR: Failed to summarize with OpenAI - {e}")
        print("⚠️ Sending raw course data instead...")
        return fallback_summary(courses)

def fallback_summary(courses):
    """Provide a fallback raw course summary."""
    fallback = "⚠️ Unable to summarize. Here are the raw course opportunities:\n\n"
    for course in courses[:5]:  # limit to top 5
        fallback += (
            f"Title: {course['title']}\n"
            f"Link: {course['link']}\n"
            f"Description: {course['description']}\n"
            f"Cost: {course['cost']}\n"
            f"Prerequisites: {course['prerequisites']}\n\n"
        )
    return fallback

def send_email(summary):
    """Send an email with the summarized training opportunities."""
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ ERROR: Missing email credentials!")
        return

    message = MIMEMultipart()
    message["From"] = EMAIL_USER
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = f"Top AI Training Opportunities - {datetime.date.today()}"

    body = (
        "Here are the top AI & medical imaging training opportunities from LinkedIn Learning, Coursera, edX, MIT, and Stanford:\n\n"
        f"{summary}"
    )
    
    message.attach(MIMEText(body, "plain"))

    try:
        print("📡 Connecting to email server...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, RECEIVER_EMAIL, message.as_string())
        server.quit()
        print("📩 Email sent successfully!")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    raw_courses = search_courses()
    if raw_courses:
        summary = summarize_and_rank(raw_courses)
        if summary:
            send_email(summary)
        else:
            print("⚠️ No summary generated.")
    else:
        print("⚠️ No relevant courses found this week.")
