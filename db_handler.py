import hashlib
from datetime import datetime, timedelta, UTC
from config import db

class MongoDBHandler:
    def __init__(self):
        self.urls_collection = db["urls"]
        self.domains_collection = db["domains"]

    def get_domains(self):
        """Fetch all domain names from the 'domains' collection."""
        return list(self.domains_collection.find({}, {"_id": 0, "url": 1}))

    def was_recently_crawled(self, url):
        """Check if a URL was crawled in the last 48 hours."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        record = self.urls_collection.find_one({"url_md5": url_hash}, {"last_crawled_date": 1})

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
                return True  

        return False

    def insert_or_update_url(self, url, text_content):
        """Store URL and extracted text in MongoDB, avoiding duplicates."""
        url_hash = hashlib.md5(url.encode()).hexdigest()

        self.urls_collection.update_one(
            {"url_md5": url_hash},  # Use URL hash to check for duplicates
            {"$setOnInsert": {"url": url}, 
             "$set": {"last_crawled_date": datetime.now(UTC), "text_content": text_content}},
            upsert=True  # Insert if not present, otherwise update timestamp and text content
        )
