from config import db

def get_processed_data(domain):
    """Retrieve stored URLs and extracted text from MongoDB."""
    urls_collection = db["urls"]
    
    # Query MongoDB for the given domain
    data = urls_collection.find({"url": {"$regex": f"^{domain}"}})
    if data:
        for record in data:
            print(f"🔹 URL: {record.get('url', 'N/A')}")
            #print(f"📄 Extracted Text: {record.get('text_content', 'No content extracted')[:300]}...")
            print(f"📧 Emails: {', '.join(record.get('emails', [])) or 'None'}")
            print(f"📞 Phone Numbers: {', '.join(record.get('phone_numbers', [])) or 'None'}")
            print(f"🧑 Names: {', '.join(record.get('names', [])) or 'None'}")
            print("-" * 50)
    else:
        print(f"❌ No data found for domain: {domain}")

# Example Usage
if __name__ == "__main__":
    domain_to_check = input("Enter the domain name to fetch data: ")
    get_processed_data(domain_to_check)
