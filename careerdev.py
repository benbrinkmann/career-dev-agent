import requests
import smtplib
import datetime
import os
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
    print("🔍 Scraping training opportunities...")

    for source in SOURCES:
        try:
            print(f"📡 Fetching: {source['name']} - {source['url']}")
            response = requests.get(source["url"], timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string.strip() if soup.title else "No title found"
            link = source["url"]
            cost = "Varies"  # Assume cost varies, could be extracted dynamically
            prerequisites = "Check link for details"

            opportunities.append({"title": title, "link": link, "cost": cost, "prerequisites": prerequisites})
        except Exception as e:
            print(f"❌ Error fetching {source['name']}: {e}")

    print(f"✅ Found {len(opportunities)} opportunities.")
    return opportunities

def send_email(opportunities):
    """Send an email with the training opportunities."""
    sender_email = os.getenv("EMAIL_USER")
    receiver_email = "benbrinkmann@gmail.com"
    password = os.getenv("EMAIL_PASS")

    if not sender_email or not password:
        print("❌ ERROR: Email credentials (EMAIL_USER, EMAIL_PASS) are missing!")
        return

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = f"AI Leadership Training - {datetime.date.today()}"

    body = "Here are the top AI leadership training and career development opportunities:\n\n"
    for opp in opportunities:
        body += f"📌 **{opp['title']}**\n🔗 Link: {opp['link']}\n💰 Cost: {opp['cost']}\n📖 Prerequisites: {opp['prerequisites']}\n\n"

    message.attach(MIMEText(body, "plain"))

    try:
        print("📡 Connecting to email server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        print("🔄 Attempting to log in...")
        server.login(sender_email, password)
        print("✅ Login successful! Sending email...")

        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("📩 Email sent successfully!")

    except smtplib.SMTPAuthenticationError:
        print("❌ ERROR: SMTP Authentication failed. Check EMAIL_PASS in GitHub Secrets.")
    except smtplib.SMTPConnectError:
        print("❌ ERROR: Unable to connect to SMTP server.")
    except smtplib.SMTPRecipientsRefused:
        print("❌ ERROR: Recipient email address was refused.")
    except Exception as e:
        print(f"❌ ERROR: {e}")

# Run the script
if __name__ == "__main__":
    opportunities = scrape_opportunities()
    if opportunities:
        send_email(opportunities)
    else:
        print("⚠️ No opportunities found. Email not sent.")
