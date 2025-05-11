import os
import hashlib
import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

# -- Configuration (set these with your Twilio sandbox info) --
account_sid = os.getenv("TWILIO_ACCOUNT_SID", "ACe963a20a0a843ff08b52d85c65224eeb")
auth_token  = os.getenv("TWILIO_AUTH_TOKEN",  "fddeb7e5098fdab07aca3c62782dc589")
twilio_number = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
target_number = os.getenv("TARGET_WHATSAPP_NUMBER", "whatsapp:+916009146526")

NDTV_URL = "https://www.ndtv.com/latest"
MAX_ARTICLES = 2  # Limit to top 10 articles

# Initialize Twilio client
client = Client(account_sid, auth_token)

def load_seen_urls(filename="seen_urls.txt"):
    if os.path.exists(filename): 
        with open(filename, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_seen_urls(seen, filename="seen_urls.txt"):
    with open(filename, "w") as f:
        for url in sorted(seen):
            f.write(url + "\n")

def get_latest_articles():
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(NDTV_URL, headers=headers, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    articles = []
    for h2 in soup.find_all("h2"):
        link = h2.find("a")
        if link and link.get("href"):
            title = link.get_text().strip()
            url = link['href'].strip()
            if title and url.startswith("http"):
                articles.append((title, url))
    return articles

def send_whatsapp_message(title, url):
    body = f"📰 *New NDTV Article:* {title}\n{url}"
    client.messages.create(
        from_=twilio_number,
        to=target_number,
        body=body
    )

def main():
    seen_urls = load_seen_urls()
    try:
        latest = get_latest_articles()
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return

    new_articles = [(title, url) for title, url in latest if url not in seen_urls]
    to_send = new_articles[:MAX_ARTICLES]

    if to_send:
        for title, url in to_send:
            print(f"Sending article: {title}")
            send_whatsapp_message(title, url)
            seen_urls.add(url)
        save_seen_urls(seen_urls)
    else:
        print("No new articles to send.")

if __name__ == "__main__":
    main()
