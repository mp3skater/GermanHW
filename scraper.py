import feedparser
import csv
import os
import re
from datetime import datetime

# The RSS feeds for the media sources you need
FEEDS = {
    "ORF News": "https://rss.orf.at/news.xml",
    "NDR Podcast": "https://www.ndr.de/nachrichten/info/podcast2998.xml"  # Streitkräfte und Strategien
}

# Create an 'articles' folder if it doesn't exist
os.makedirs("articles", exist_ok=True)

# Create a filename with today's date
today_str = datetime.now().strftime("%Y-%m-%d")
filename = f"articles/news_{today_str}.csv"


def clean_html(raw_html):
    """Removes annoying HTML tags from the content summary"""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()


with open(filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write the header row to match your assignment table
    writer.writerow(["Medium", "Datum", "Titel", "URL", "Inhalt", "Kurzkommentar"])

    for source, url in FEEDS.items():
        parsed_feed = feedparser.parse(url)

        # We only grab the top 10 articles per source per day so you have choices, but aren't overwhelmed
        for entry in parsed_feed.entries[:10]:
            title = entry.get("title", "Kein Titel")
            link = entry.get("link", "")

            # Formats the date nicely
            date = entry.get("published", "")

            # Gets the summary and cleans out HTML tags
            content_raw = entry.get("summary", "")
            content_clean = clean_html(content_raw)

            # Write the row (Leaving Kurzkommentar blank for you to fill in later)
            writer.writerow([source, date, title, link, content_clean, ""])

print(f"Success! Saved daily articles to {filename}")