import requests
import smtplib
import datetime
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Define search sources
SOURCES = [
    {"name": "Coursera AI for Medicine", "url": "https://www.coursera.org/specializations/ai-for-medicine"},
    {"name": "MICCAI Conferences", "url": "https://www.miccai.org"},
    {"name": "MIT AI Leadership", "url": "https://executive.mit.edu"},
    {"name": "Stanford AI Healthcare", "url": "https://ai100.stanford.edu"},
    {"name": "Epilepsy Foundation Research", "url": "https://www.epilepsy.com/research-training"}
]

def scrape_opportunities():
    """Scrape basic data from defined sources."""
    opportunities = []
    for source in SOURCES:
        try:
            response = requests.get(source["url"], timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "No title found"
            link = source["url"]
            cost = "Varies"  # Assume cost varies, could be extracted dynamically
            prerequisites = "Check link for details"
            opportunities.append({"title": title, "link": link, "cost": cost, "prerequisites": prerequisites})
        except Exception as e:
            print(f"Error fetching {source['name']}: {e}")
    return opportunities

def send_email(opportunities):
    """Send an email with the training opportunities."""
    sender_email = "your-email@gmail.com"
    receiver_email = "benbrinkmann@gmail.com"
    password = "your-email-password"  # Use an app password or environment variable!

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"AI Leadership Training - {datetime.date.today()}"
