import feedparser
import csv
import os
import re
import ssl
import time

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

# The SINGLE file where everything will be saved forever
filename = "alle_artikel.csv"


def clean_text(raw_html):
    """Removes HTML tags and cleans up messy line breaks for Excel."""
    if not raw_html:
        return ""
    cleanr = re.compile('<.*?>')
    text = re.sub(cleanr, '', raw_html)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# --- 1. SMART MEMORY: Read existing URLs to prevent duplicates ---
existing_urls = set()
file_exists = os.path.isfile(filename)

if file_exists:
    with open(filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        try:
            next(reader)  # Skip the header row
            for row in reader:
                if len(row) > 3:
                    existing_urls.add(row[3])  # The URL is in the 4th column (Index 3)
        except StopIteration:
            pass

# --- 2. Scrape and Append ---
try:
    # Notice mode='a' (append). This adds to the bottom of the file!
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Only write the header if the file is being created for the very first time
        if not file_exists:
            writer.writerow(["Medium", "Datum", "Titel", "URL", "Inhalt", "Kurzkommentar"])

        for source, url in FEEDS.items():
            print(f"Downloading news from {source}...")
            parsed_feed = feedparser.parse(url)

            if not parsed_feed.entries:
                print(f"WARNING: Could not find any articles for {source}.")
                continue

            saved_articles = 0

            for entry in parsed_feed.entries:
                # STOP IF WE ALREADY GOT 1 ARTICLES FOR THIS SOURCE
                if saved_articles >= 1:
                    break

                title = entry.get("title", "Kein Titel")
                link = entry.get("link", "")

                # If we already have this article in our CSV, skip it!
                if link in existing_urls:
                    continue

                # Get Date
                date_str = ""
                if "published_parsed" in entry and entry.published_parsed:
                    date_str = time.strftime("%d.%m.%Y", entry.published_parsed)
                elif "updated_parsed" in entry and entry.updated_parsed:
                    date_str = time.strftime("%d.%m.%Y", entry.updated_parsed)
                else:
                    date_str = entry.get("published", entry.get("updated", "Kein Datum"))

                # Get Content
                content_raw = ""
                if "summary" in entry:
                    content_raw = entry.summary
                elif "content" in entry and len(entry.content) > 0:
                    content_raw = entry.content[0].get("value", "")
                elif "description" in entry:
                    content_raw = entry.description

                content_clean = clean_text(content_raw)

                # Skip useless empty breaking news
                if not content_clean or content_clean == "":
                    continue

                # Save it to the CSV
                writer.writerow([source, date_str, title, link, content_clean, ""])
                existing_urls.add(link)  # Add to memory so we don't save it twice
                saved_articles += 1

            print(f"Successfully added {saved_articles} NEW articles from {source}!")

    print(f"\nSUCCESS! All done. Open {filename} to see your list.")

except Exception as e:
    print(f"\nCRITICAL ERROR: Something went wrong!\nError Details: {e}")
