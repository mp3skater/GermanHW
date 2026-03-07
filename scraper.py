import feedparser
import csv
import os
import re
import ssl
from datetime import datetime

# --- Mac SSL Fix ---
# This prevents Mac computers from blocking the download
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
# -------------------

FEEDS = {
    "ORF News": "https://rss.orf.at/news.xml",
    "NDR Podcast": "https://www.ndr.de/nachrichten/info/podcast2998.xml"
}

print("Starting the news scraper...")

os.makedirs("articles", exist_ok=True)
today_str = datetime.now().strftime("%Y-%m-%d")
filename = f"articles/news_{today_str}.csv"


def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()


try:
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Medium", "Datum", "Titel", "URL", "Inhalt", "Kurzkommentar"])

        for source, url in FEEDS.items():
            print(f"Downloading news from {source}...")
            parsed_feed = feedparser.parse(url)

            # Check if feed actually downloaded
            if not parsed_feed.entries:
                print(f"WARNING: Could not find any articles for {source}. URL might be wrong or blocked.")
                continue

            for entry in parsed_feed.entries[:10]:
                title = entry.get("title", "Kein Titel")
                link = entry.get("link", "")
                date = entry.get("published", "")

                content_raw = entry.get("summary", "")
                content_clean = clean_html(content_raw)

                writer.writerow([source, date, title, link, content_clean, ""])

            print(f"Successfully saved articles from {source}!")

    print(f"\nSUCCESS! All done. Open {filename} to see your news.")

except Exception as e:
    print(f"\nCRITICAL ERROR: Something went wrong!\nError Details: {e}")