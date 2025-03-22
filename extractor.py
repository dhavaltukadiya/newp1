import re
import phonenumbers
import spacy
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class ContentExtractor:

    nlp = spacy.load("en_core_web_trf")

    @staticmethod
    def extract_text(html):
        """Extract visible text from HTML."""
        soup = BeautifulSoup(html, "lxml")
        return ' '.join(soup.stripped_strings)  # Extracts and joins visible text

    @staticmethod
    def extract_links(html, base_url):
        """Extract all internal links from a webpage."""
        soup = BeautifulSoup(html, "lxml")
        links = set()

        for a_tag in soup.find_all("a", href=True):
            href = urljoin(base_url, a_tag["href"])
            if urlparse(href).netloc == urlparse(base_url).netloc:
                links.add(href)
        
        return links

    @staticmethod
    def extract_emails(text):
        """Extract emails from text."""
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        return list(set(re.findall(email_pattern, text)))

    @staticmethod
    def extract_phone_numbers(text):
        """Extract only valid USA phone numbers and remove duplicates."""
        phone_numbers = set()  # Use set to avoid duplicates

        for match in re.findall(r"\+?\d[\d\s().-]{8,}\d", text):
            try:
                parsed_number = phonenumbers.parse(match, "US")  
                if phonenumbers.is_valid_number(parsed_number) and phonenumbers.region_code_for_number(parsed_number) == "US":
                    formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    phone_numbers.add(formatted_number)  # Add to set
            except phonenumbers.NumberParseException:
                continue

        return list(phone_numbers)  # Convert set back to list

    @staticmethod
    def extract_names(text):
        """Extract unique person names using spaCy, filtering common words."""
        
        doc = ContentExtractor.nlp(text)
    
        # Extract only unique PERSON entities
        names = set(ent.text for ent in doc.ents if ent.label_ == "PERSON")

        # Optional: Remove unwanted words (e.g., menu items, common words)
        ignore_words = {"Weather", "Blog", "Subscribe", "Connect@"}
        cleaned_names = [name for name in names if name not in ignore_words]

        return list(cleaned_names)  # Convert set back to list

