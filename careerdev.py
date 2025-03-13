import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import openai

# Extract credentials from environment variables
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
RECEIVER_EMAIL = "benbrinkmann@gmail.com"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

# Set OpenAI key
openai.api_key = OPENAI_API_KEY

def search_ai_training_opportunities():
    print("🔍 Searching for AI Training Opportunities via SerpAPI...")

    params = {
        "engine": "google",
        "q": "AI leadership courses OR medical imaging AI training OR neurology AI online course",
        "hl": "en",
        "num": 10,
        "api_key": SERPAPI_API_KEY
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to fetch results from SerpAPI - {e}")
        return []

    opportunities = []
    if "organic_results" in data:
        for result in data["organic_results"][:10]:
            opportunities.append({
                "title": result.get("title", "No title found"),
                "link": result.get("link", "No link found"),
                "snippet": result.get("snippet", "No description found")
            })

    print(f"✅ Found {len(opportunities)} training opportunities.")
    return opportunities

def summarize_and_rank(opportunities):
    print("🤖 Summarizing and ranking training opportunities with ChatGPT...")

    if not OPENAI_API_KEY:
        print("❌ ERROR: Missing OpenAI API Key!")
        return fallback_summary(opportunities)

    prompt = (
        "You are an expert career advisor. Summarize and rank the following AI leadership and medical imaging training opportunities."
        " Summarize the top 5 with title, summary, relevance, and value.\n\n"
    )

    for opportunity in opportunities:
        prompt += f"Title: {opportunity['title']}\nLink: {opportunity['link']}\nDescription: {opportunity['snippet']}\n\n"

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
        return fallback_summary(opportunities)

def fallback_summary(opportunities):
    fallback = "⚠️ Unable to summarize. Here are the raw AI training opportunities:\n\n"
    for opportunity in opportunities[:5]:
        fallback += (
            f"Title: {opportunity['title']}\n"
            f"Link: {opportunity['link']}\n"
            f"Description: {opportunity['snippet']}\n\n"
        )
    return fallback

def send_email(summary):
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ ERROR: Missing email credentials!")
        return

    message = MIMEMultipart()
    message["From"] = EMAIL_USER
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = f"Top AI Training Opportunities - {datetime.date.today()}"

    body = (
        "Here are the latest AI leadership and medical imaging training opportunities:\n\n"
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
    opportunities = search_ai_training_opportunities()
    if opportunities:
        summary = summarize_and_rank(opportunities)
        if summary:
            send_email(summary)
        else:
            print("⚠️ No summary generated.")
    else:
        print("⚠️ No opportunities found.")
