import os
import smtplib
import datetime
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    import requests
except ImportError:
    print("❌ ERROR: 'requests' module is not installed. Please install it using 'pip install requests'")
    exit()

# Define search parameters
SEARCH_QUERY = "AI leadership OR medical imaging site:linkedin.com/learning"
SEARCH_ENGINE_URL = "https://www.bing.com/search?q="

# Extract email credentials from environment variables
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
RECEIVER_EMAIL = "benbrinkmann@gmail.com"

def search_courses():
    """Search LinkedIn Learning and extract top 5 courses."""
    print("🔍 Searching for AI & Medical Imaging training...")
    try:
        response = requests.get(SEARCH_ENGINE_URL + SEARCH_QUERY, timeout=10)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Network issue - Unable to reach the search engine. Check your internet connection or API restrictions.")
        return []
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out. Try increasing the timeout period.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Unable to fetch search results - {e}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    print(f"soup returned {len(soup)} ")

    courses = []
    for result in soup.find_all("li", class_="b_algo")[:5]:
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
    
    print(f"✅ Found {len(courses)} courses.")
    return courses

def send_email(courses):
    """Send an email with the top training opportunities."""
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ ERROR: Missing email credentials!")
        return

    message = MIMEMultipart()
    message["From"] = EMAIL_USER
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = f"Top AI Training Opportunities - {datetime.date.today()}"

    body = "Here are the top AI & medical imaging training opportunities from LinkedIn Learning and other sources:\n\n"
    for course in courses:
        body += f"📌 **{course['title']}**\n🔗 Link: {course['link']}\n📖 Description: {course['description']}\n💰 Cost: {course['cost']}\n📖 Prerequisites: {course['prerequisites']}\n\n"
    
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
    courses = search_courses()
    if courses:
        send_email(courses)
    else:
        print("⚠️ No relevant courses found this week.")
