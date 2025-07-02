#!/usr/bin/env python3
"""
Wikipedia Scraper for Alexander the Great
Extracts structured content from Wikipedia page preserving headings and subheadings.
"""

import requests
from bs4 import BeautifulSoup
import re
import os
import json
from typing import Dict, List


class WikipediaScraper:
    SKIP_SECTIONS = {'Contents', 'References', 'External links', 'See also', 'Further reading', 'Notes'}

    def __init__(self, url: str):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.content_dict = {}

    def fetch_page(self) -> BeautifulSoup:
        """Fetch the Wikipedia page and return BeautifulSoup object."""
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch page: {e}")

    def clean_text(self, text: str) -> str:
        """Clean text by removing citation numbers and extra whitespace."""
        text = re.sub(r'\[\d+\]', '', text)  # Remove [1], [2] etc.
        return ' '.join(text.split()).strip()

    def is_content_significant(self, text: str, min_length: int = 50) -> bool:
        """Check if paragraph content is significant enough to include."""
        return len(text.strip()) >= min_length

    def extract_content(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Extract structured content from Wikipedia page."""
        content_div = soup.find('div', {'id': 'mw-content-text'})
        if not content_div:
            raise Exception("Could not find main content area")

        current_h2 = "Introduction"
        current_h3 = None
        content_dict = {}

        elements = content_div.find_all(['h2', 'h3', 'p'])

        for element in elements:
            if element.name == 'h2':
                heading_text = element.get_text(strip=True).replace('[edit]', '')
                if heading_text in self.SKIP_SECTIONS:
                    current_h2 = None
                    current_h3 = None
                    continue

                current_h2 = self.clean_text(heading_text)
                current_h3 = None
                content_dict.setdefault(current_h2, [])

            elif element.name == 'h3':
                heading_text = element.get_text(strip=True).replace('[edit]', '')
                current_h3 = self.clean_text(heading_text)

            elif element.name == 'p':
                para_text = self.clean_text(element.get_text())
                if not self.is_content_significant(para_text):
                    continue

                if any(skip in para_text.lower() for skip in ['coordinates:', 'wikimedia commons', 'category:', 'this article']):
                    continue

                if current_h2 is None:
                    continue  # Skip paragraphs under skipped sections

                section_key = f"{current_h2} > {current_h3}" if current_h3 else current_h2
                content_dict.setdefault(section_key, []).append(para_text)

        return content_dict

    def format_output(self, content_dict: Dict[str, List[str]]) -> str:
        """Format the extracted content into readable Markdown-like text."""
        output = []
        for section, paragraphs in content_dict.items():
            if not paragraphs:
                continue

            header_prefix = "###" if '>' in section else "##"
            output.append(f"\n{header_prefix} {section}")
            for para in paragraphs:
                output.append(f"\n{para}")
            output.append("")  # Blank line

        return '\n'.join(output).strip()

    def save_to_file(self, content: str, filename: str = "raw_wiki_content.txt"):
        """Save text content to file."""
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[+] Markdown content saved to: {filepath} ({len(content)} characters)")
        except IOError as e:
            raise Exception(f"Failed to save file: {e}")

    def save_as_json(self, content_dict: Dict[str, List[str]], filename: str = "raw_wiki_content.json"):
        """Save content dictionary as JSON."""
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        filepath = os.path.join(data_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content_dict, f, indent=2, ensure_ascii=False)
            print(f"[+] JSON content saved to: {filepath}")
        except IOError as e:
            raise Exception(f"Failed to save JSON file: {e}")

    def scrape(self):
        """Main scraping method that orchestrates the entire process."""
        print("[*] Fetching Wikipedia page...")
        soup = self.fetch_page()

        print("[*] Extracting content...")
        self.content_dict = self.extract_content(soup)
        print(f"[+] Extracted {len(self.content_dict)} sections")

        print("[*] Formatting for output...")
        formatted_content = self.format_output(self.content_dict)

        print("[*] Saving outputs...")
        self.save_to_file(formatted_content)
        self.save_as_json(self.content_dict)

        return formatted_content


def main():
    """Entry point."""
    url = "https://en.wikipedia.org/wiki/Alexander_the_Great"

    try:
        scraper = WikipediaScraper(url)
        content = scraper.scrape()

        print("\n" + "="*50)
        print("SCRAPING COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Sections extracted: {len(scraper.content_dict)}")
        print("Markdown Output: data/raw_wiki_content.txt")
        print("JSON Output:     data/raw_wiki_content.json")

        # Preview first few lines
        print("\nPreview (first 10 lines):")
        print("-" * 30)
        for line in content.split('\n')[:10]:
            print(line)
        print("...")

    except Exception as e:
        print(f"[!] Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
