import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta, UTC
from config import db
import hashlib
from extractor import ContentExtractor

def get_domains():
    """Fetch domains from the database."""
    return db.domains.find({}, {"_id": 0, "url": 1})

def should_crawl(url):
    """Check if a URL was crawled in the last 48 hours."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    record = db.urls.find_one({"url_md5": url_hash}, {"last_crawled_date": 1})

    if record and "last_crawled_date" in record:
        last_crawled_date = record["last_crawled_date"]

        # Convert to datetime if stored as string
        if isinstance(last_crawled_date, str):
            last_crawled_date = datetime.fromisoformat(last_crawled_date)

        # Ensure datetime is in UTC
        if last_crawled_date.tzinfo is None:
            last_crawled_date = last_crawled_date.replace(tzinfo=UTC)

        # Skip if crawled within 48 hours
        if last_crawled_date >= datetime.now(UTC) - timedelta(hours=48):
            return False  

    return True

def store_url(url, text_content):
    """Store URL and extracted text in MongoDB, avoiding duplicates."""
    url_hash = hashlib.md5(url.encode()).hexdigest()

    db.urls.update_one(
        {"url_md5": url_hash},  # Use URL hash to check for duplicates
        {"$setOnInsert": {"url": url}, "$set": {"last_crawled_date": datetime.now(UTC), "text_content": text_content}},
        upsert=True  # Insert if not present, otherwise update timestamp and text content
    )

def fetch_html(url):
    """Download the webpage HTML content."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

def extract_text(html):
    """Extract visible text from HTML."""
    soup = BeautifulSoup(html, "lxml")
    return ' '.join(soup.stripped_strings)  # Extracts and joins visible text

def extract_links(html, base_url):
    """Extract all internal links from a webpage."""
    soup = BeautifulSoup(html, "lxml")
    for a_tag in soup.find_all("a", href=True):
        href = urljoin(base_url, a_tag["href"])
        if urlparse(href).netloc == urlparse(base_url).netloc:
            yield href  # Generator to save memory

def crawl_website():
    """Crawl websites dynamically from MongoDB."""
    domains = list(get_domains())

    if not domains:
        print("No domains found in the database.")
        return

    crawled_any = False

    for domain in domains:
        domain_url = domain["url"]

        if not should_crawl(domain_url):
            print(f"Skipping (Already Crawled): {domain_url}")
            continue  

        print(f"Crawling: {domain_url}")
        html = fetch_html(domain_url)
        if not html:
            continue

        text_content = extract_text(html)  # Extract text
        store_url(domain_url, text_content)  # Store domain URL with text
        crawled_any = True  # At least one URL is crawled

        for link in extract_links(html, domain_url):
            if should_crawl(link):
                print(f" - Found: {link}")
                link_html = fetch_html(link)
                link_text = extract_text(link_html) if link_html else ""
                store_url(link, link_text)

    if not crawled_any:
        print("✅ All links are already crawled within the last 48 hours.")


def store_url(url, text_content):
    """Store URL and extracted text in MongoDB, avoiding duplicates."""
    url_hash = hashlib.md5(url.encode()).hexdigest()
    
    extracted_emails = ContentExtractor.extract_emails(text_content)
    extracted_phones = ContentExtractor.extract_phone_numbers(text_content)
    extracted_names = ContentExtractor.extract_names(text_content)

    db.urls.update_one(
        {"url_md5": url_hash},  
        {
            "$setOnInsert": {"url": url},
            "$set": {
                "last_crawled_date": datetime.now(UTC),
                "text_content": text_content,
                "emails": extracted_emails,
                "phone_numbers": extracted_phones,
                "names": extracted_names,
            },
        },
        upsert=True
    )


if __name__ == "__main__":
    crawl_website()
