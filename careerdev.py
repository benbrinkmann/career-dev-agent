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

def search_scholar_papers():
    print("🔍 Searching Google Scholar via SerpAPI...")

    params = {
        "engine": "google_scholar",
        "q": "epilepsy OR seizure EEG OR MRI OR MEG OR PET OR AI OR Machine learning",
        "hl": "en",
        "api_key": SERPAPI_API_KEY
    }

    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to fetch results from SerpAPI - {e}")
        return []

    papers = []
    if "organic_results" in data:
        for result in data["organic_results"][:10]:
            papers.append({
                "title": result.get("title", "No title found"),
                "link": result.get("link", "No link found"),
                "snippet": result.get("snippet", "No description found")
            })

    print(f"✅ Found {len(papers)} papers.")
    return papers

def summarize_and_rank(papers):
    print("🤖 Summarizing and ranking papers with ChatGPT...")

    if not OPENAI_API_KEY:
        print("❌ ERROR: Missing OpenAI API Key!")
        return fallback_summary(papers)

    prompt = (
        "You are an expert neuroscientist. Summarize and rank the following research papers "
        "on epilepsy and neurotechnology. Summarize the top 5 with title, summary, relevance.\n\n"
    )

    for paper in papers:
        prompt += f"Title: {paper['title']}\nLink: {paper['link']}\nDescription: {paper['snippet']}\n\n"

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You summarize neuroscience papers."},
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
        return fallback_summary(papers)

def fallback_summary(papers):
    fallback = "⚠️ Unable to summarize. Here are the raw research papers:\n\n"
    for paper in papers[:5]:
        fallback += (
            f"Title: {paper['title']}\n"
            f"Link: {paper['link']}\n"
            f"Description: {paper['snippet']}\n\n"
        )
    return fallback

def send_email(summary):
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ ERROR: Missing email credentials!")
        return

    message = MIMEMultipart()
    message["From"] = EMAIL_USER
    message["To"] = RECEIVER_EMAIL
    message["Subject"] = f"New Neurotech Papers - {datetime.date.today()}"

    body = (
        "Here are the latest epilepsy & neurotech research papers:\n\n"
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
    papers = search_scholar_papers()
    if papers:
        summary = summarize_and_rank(papers)
        if summary:
            send_email(summary)
        else:
            print("⚠️ No summary generated.")
    else:
        print("⚠️ No papers found.")
