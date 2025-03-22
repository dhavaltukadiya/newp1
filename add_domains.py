from config import db

def add_domains():
    """Allow the user to enter multiple domains and store them in MongoDB."""
    while True:
        domain = input("Enter a domain to add (or type 'done' to finish): ").strip()

        if domain.lower() == "done":
            break  # Stop taking input

        if domain and not db.domains.find_one({"url": domain}):
            db.domains.insert_one({"url": domain})
            print(f"✅ Added: {domain}")
        else:
            print(f"⚠️ Already Exists or Invalid Input: {domain}")

if __name__ == "__main__":
    add_domains()
