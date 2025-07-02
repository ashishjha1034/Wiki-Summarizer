#!/usr/bin/env python3
"""
AI Summarizer for Wikipedia Content
Uses Groq's LLaMA 3.1 8B model to summarize extracted Wikipedia sections.
"""

import json
import os
import time
import requests
from typing import Dict, List, Optional
from dotenv import load_dotenv


class GroqSummarizer:
    def __init__(self, api_key: str, model: str = "llama-3.1-8b-instant"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.min_section_length = 50  # Skip very short sections
        self.max_retries = 3
        self.base_delay = 1  # Base delay for exponential backoff
    
    def load_json_data(self, filepath: str) -> Dict[str, List[str]]:
        """Load JSON data from file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✓ Loaded data from {filepath}")
            print(f"  Found {len(data)} sections")
            return data
        except FileNotFoundError:
            raise Exception(f"JSON file not found: {filepath}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON format: {e}")
        except Exception as e:
            raise Exception(f"Error loading JSON: {e}")
    
    def prepare_section_text(self, paragraphs: List[str]) -> str:
        """Concatenate paragraphs into a single text block."""
        return '\n\n'.join(paragraphs).strip()
    
    def is_section_valid(self, section_text: str) -> bool:
        """Check if section has enough content to summarize."""
        return len(section_text.strip()) >= self.min_section_length
    
    def create_prompt(self, section_text: str) -> List[Dict[str, str]]:
        """Create the messages payload for Groq API."""
        return [
            {
                "role": "system",
                "content": "You are a helpful summarizer. Provide concise, accurate summaries that capture the key information and main points."
            },
            {
                "role": "user",
                "content": f"Summarize the following text in 2–4 concise, coherent sentences. Focus on the main points and key information:\n\n{section_text}"
            }
        ]
    
    def call_groq_api(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """Make API call to Groq with retry logic."""
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,  # Lower temperature for more consistent summaries
            "max_tokens": 200,   # Limit response length
            "top_p": 0.9
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                
                elif response.status_code == 429:  # Rate limit
                    wait_time = self.base_delay * (2 ** attempt)
                    print(f"  ⚠ Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    print(f"  ⚠ API error {response.status_code}: {response.text}")
                    if attempt < self.max_retries - 1:
                        wait_time = self.base_delay * (2 ** attempt)
                        print(f"  Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    continue
                        
            except requests.exceptions.Timeout:
                print(f"  ⚠ Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay * (2 ** attempt))
                continue
                
            except requests.exceptions.RequestException as e:
                print(f"  ⚠ Request error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.base_delay * (2 ** attempt))
                continue
        
        return None
    
    def summarize_section(self, section_name: str, paragraphs: List[str]) -> Optional[str]:
        """Summarize a single section."""
        # Prepare the text
        section_text = self.prepare_section_text(paragraphs)
        
        # Check if section is worth summarizing
        if not self.is_section_valid(section_text):
            print(f"  ⚠ Skipping '{section_name}' (too short: {len(section_text)} chars)")
            return None
        
        # Create prompt
        messages = self.create_prompt(section_text)
        
        # Call API
        print(f"  📡 Calling Groq API for '{section_name}'...")
        summary = self.call_groq_api(messages)
        
        if summary:
            print(f"  ✓ Summarized '{section_name}'")
            return summary
        else:
            print(f"  ✗ Failed to summarize '{section_name}'")
            return None
    
    def format_markdown_output(self, summaries: Dict[str, str]) -> str:
        """Format summaries into Markdown."""
        output_lines = []
        
        for section_name, summary in summaries.items():
            # Determine heading level based on section structure
            if '>' in section_name:
                # This is a subsection
                output_lines.append(f"### {section_name}\n")
            else:
                # This is a main section
                output_lines.append(f"## {section_name}\n")
            
            output_lines.append(f"{summary}\n")
        
        return '\n'.join(output_lines).strip()
    
    def save_markdown(self, content: str, filepath: str):
        """Save content to Markdown file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Saved summaries to {filepath}")
        except Exception as e:
            raise Exception(f"Failed to save markdown file: {e}")
    
    def process_all_sections(self, input_file: str, output_file: str):
        """Main processing pipeline."""
        print("🚀 Starting summarization process...")
        print("=" * 50)
        
        # Load data
        data = self.load_json_data(input_file)
        
        # Process each section
        summaries = {}
        total_sections = len(data)
        processed = 0
        
        print(f"\n📝 Processing {total_sections} sections...")
        print("-" * 30)
        
        for section_name, paragraphs in data.items():
            print(f"[{processed + 1}/{total_sections}] Processing '{section_name}'...")
            
            summary = self.summarize_section(section_name, paragraphs)
            
            if summary:
                summaries[section_name] = summary
                processed += 1
            
            # Small delay to be respectful to API
            time.sleep(0.5)
        
        print(f"\n✓ Successfully processed {processed}/{total_sections} sections")
        
        if summaries:
            # Format and save
            print("\n📄 Formatting Markdown output...")
            markdown_content = self.format_markdown_output(summaries)
            
            print("💾 Saving to file...")
            self.save_markdown(markdown_content, output_file)
            
            print("\n" + "=" * 50)
            print("🎉 SUMMARIZATION COMPLETED!")
            print("=" * 50)
            print(f"Input file: {input_file}")
            print(f"Output file: {output_file}")
            print(f"Sections processed: {processed}")
            print(f"Total characters: {len(markdown_content)}")
            
            # Show preview
            lines = markdown_content.split('\n')[:8]
            print("\nPreview:")
            print("-" * 20)
            for line in lines:
                print(line)
            if len(markdown_content.split('\n')) > 8:
                print("...")
        
        else:
            print("\n⚠ No sections were successfully summarized!")
        
        return summaries


def load_environment():
    """Load environment variables from .env file."""
    load_dotenv()
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise Exception(
            "GROQ_API_KEY not found in environment variables. "
            "Please create a .env file with: GROQ_API_KEY=your_api_key_here"
        )
    
    return api_key


def main():
    """Main function to run the summarizer."""
    try:
        # Load API key
        print("🔐 Loading API credentials...")
        api_key = load_environment()
        
        # Initialize summarizer
        summarizer = GroqSummarizer(api_key)
        
        # Define file paths
        input_file = "data/raw_wiki_content.json"
        output_file = "data/summarized_output.md"
        
        # Process sections
        summaries = summarizer.process_all_sections(input_file, output_file)
        
        return 0 if summaries else 1
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())