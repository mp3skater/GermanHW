import feedparser
import csv
import os
import re
import ssl
import time
from datetime import datetime

# --- Mac SSL Fix ---
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


def clean_text(raw_html):
    """Removes HTML tags and cleans up messy line breaks for Excel."""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    text = re.sub(cleanr, '', raw_html)
    # Replace weird newlines and tabs with normal spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


try:
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Medium", "Datum", "Titel", "URL", "Inhalt", "Kurzkommentar"])

        for source, url in FEEDS.items():
            print(f"Downloading news from {source}...")
            parsed_feed = feedparser.parse(url)

            if not parsed_feed.entries:
                print(f"WARNING: Could not find any articles for {source}.")
                continue

            saved_articles = 0

            # We look at up to 40 articles to ensure we find 10 GOOD ones
            for entry in parsed_feed.entries[:40]:
                if saved_articles >= 10:
                    break  # We have our 10 full articles, move to the next news source!

                title = entry.get("title", "Kein Titel")
                link = entry.get("link", "")

                # --- 1. Fix the Date Issue ---
                date_str = ""
                # Try to grab the parsed time and format it nicely (DD.MM.YYYY)
                if "published_parsed" in entry and entry.published_parsed:
                    date_str = time.strftime("%d.%m.%Y", entry.published_parsed)
                elif "updated_parsed" in entry and entry.updated_parsed:
                    date_str = time.strftime("%d.%m.%Y", entry.updated_parsed)
                else:
                    # Fallback if the parser fails
                    date_str = entry.get("published", entry.get("updated", "Kein Datum"))

                # --- 2. Fix the Content Issue ---
                content_raw = ""
                # Check all the different ways RSS feeds hide their text
                if "summary" in entry:
                    content_raw = entry.summary
                elif "content" in entry and len(entry.content) > 0:
                    content_raw = entry.content[0].get("value", "")
                elif "description" in entry:
                    content_raw = entry.description

                content_clean = clean_text(content_raw)

                # Skip articles that have no content (e.g. ORF Breaking News)
                if not content_clean or content_clean == "":
                    continue

                # If it passed the checks, save it to the CSV!
                writer.writerow([source, date_str, title, link, content_clean, ""])
                saved_articles += 1

            print(f"Successfully saved {saved_articles} full articles from {source}!")

    print(f"\nSUCCESS! All done. Open {filename} to see your perfect CSV.")

except Exception as e:
    print(f"\nCRITICAL ERROR: Something went wrong!\nError Details: {e}")