#!/usr/bin/env python3
"""
Complete Wikipedia-to-Summary Pipeline
Orchestrates the full workflow: Wikipedia scraping → AI summarization → Markdown output
"""

import os
import sys
import json
import time
from pathlib import Path

# Import our custom modules
try:
    from scraper import WikipediaScraper
    from summarizer import GroqSummarizer, load_environment
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure scraper.py and summarizer.py are in the same directory")
    sys.exit(1)


class WikiPipeline:
    """Main pipeline class that orchestrates the complete workflow."""
    
    def __init__(self, wikipedia_url: str):
        self.wikipedia_url = wikipedia_url
        self.data_dir = Path("data")
        self.json_file = self.data_dir / "raw_wiki_content.json"
        self.txt_file = self.data_dir / "raw_wiki_content.txt"
        self.markdown_file = self.data_dir / "summarized_output.md"
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
    
    def step_1_scraping(self) -> bool:
        """Step 1: Scrape Wikipedia content."""
        print("🔍 STEP 1: Scraping Wikipedia content...")
        print("-" * 50)
        
        try:
            # Initialize scraper
            scraper = WikipediaScraper(self.wikipedia_url)
            
            # Run scraping process
            content = scraper.scrape()
            
            # Convert the structured content to JSON format for the summarizer
            self._convert_txt_to_json(scraper.content_dict)
            
            print("✅ Scraping completed successfully!")
            print(f"   📄 Text file: {self.txt_file}")
            print(f"   📋 JSON file: {self.json_file}")
            print(f"   📊 Sections found: {len(scraper.content_dict)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            return False
    
    def _convert_txt_to_json(self, content_dict: dict):
        """Convert the scraper's content dictionary to JSON format."""
        try:
            with open(self.json_file, 'w', encoding='utf-8') as f:
                json.dump(content_dict, f, indent=2, ensure_ascii=False)
            print(f"   💾 Saved JSON data: {self.json_file}")
        except Exception as e:
            raise Exception(f"Failed to save JSON file: {e}")
    
    def step_2_load_api_key(self) -> str:
        """Step 2: Load Groq API key from environment."""
        print("\n🔐 STEP 2: Loading API credentials...")
        print("-" * 50)
        
        try:
            api_key = load_environment()
            print("✅ API key loaded successfully!")
            return api_key
            
        except Exception as e:
            print(f"❌ Failed to load API key: {e}")
            print("   Make sure you have a .env file with GROQ_API_KEY=your_key")
            raise
    
    def step_3_summarization(self, api_key: str) -> bool:
        """Step 3: Generate AI summaries using Groq."""
        print("\n🧠 STEP 3: Generating AI summaries...")
        print("-" * 50)
        
        try:
            # Check if JSON file exists
            if not self.json_file.exists():
                raise Exception(f"JSON file not found: {self.json_file}")
            
            # Initialize summarizer
            summarizer = GroqSummarizer(api_key)
            
            # Run summarization process
            summaries = summarizer.process_all_sections(
                str(self.json_file), 
                str(self.markdown_file)
            )
            
            if summaries:
                print("✅ Summarization completed successfully!")
                print(f"   📝 Output file: {self.markdown_file}")
                print(f"   📊 Sections summarized: {len(summaries)}")
                return True
            else:
                print("⚠️  No summaries were generated")
                return False
                
        except Exception as e:
            print(f"❌ Summarization failed: {e}")
            return False
    
    def generate_pipeline_report(self, success: bool, start_time: float):
        """Generate a final pipeline report."""
        duration = time.time() - start_time
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        else:
            print("💥 PIPELINE COMPLETED WITH ERRORS!")
        print("=" * 60)
        
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        print(f"🌐 Wikipedia URL: {self.wikipedia_url}")
        print(f"📁 Data directory: {self.data_dir}")
        
        # Show file status
        print("\n📋 Generated Files:")
        files_to_check = [
            (self.txt_file, "Raw text content"),
            (self.json_file, "Structured JSON data"),
            (self.markdown_file, "AI summaries (Markdown)")
        ]
        
        for file_path, description in files_to_check:
            if file_path.exists():
                size = file_path.stat().st_size
                print(f"   ✅ {description}: {file_path} ({size:,} bytes)")
            else:
                print(f"   ❌ {description}: {file_path} (missing)")
        
        if success:
            print("\n🚀 Ready to use your summarized Wikipedia content!")
            print(f"   Open: {self.markdown_file}")
        else:
            print("\n🔧 Check the error messages above and try again.")


def run_pipeline(wikipedia_url: str = "https://en.wikipedia.org/wiki/Alexander_the_Great") -> bool:
    """
    Main pipeline function that orchestrates the complete workflow.
    
    Args:
        wikipedia_url: URL of the Wikipedia page to process
        
    Returns:
        bool: True if pipeline completed successfully, False otherwise
    """
    start_time = time.time()
    pipeline = WikiPipeline(wikipedia_url)
    
    print("🚀 STARTING WIKIPEDIA-TO-SUMMARY PIPELINE")
    print("=" * 60)
    print(f"🎯 Target: {wikipedia_url}")
    print(f"📂 Output directory: {pipeline.data_dir}")
    print()
    
    try:
        # Step 1: Scrape Wikipedia content
        if not pipeline.step_1_scraping():
            pipeline.generate_pipeline_report(False, start_time)
            return False
        
        # Brief pause between steps
        time.sleep(1)
        
        # Step 2: Load API credentials
        api_key = pipeline.step_2_load_api_key()
        
        # Brief pause before API calls
        time.sleep(1)
        
        # Step 3: Generate summaries
        success = pipeline.step_3_summarization(api_key)
        
        # Generate final report
        pipeline.generate_pipeline_report(success, start_time)
        
        return success
        
    except KeyboardInterrupt:
        print("\n⏹️  Pipeline interrupted by user")
        pipeline.generate_pipeline_report(False, start_time)
        return False
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        pipeline.generate_pipeline_report(False, start_time)
        return False


def main():
    """Main entry point with command line argument support."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Complete Wikipedia-to-Summary Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py
  python pipeline.py --url "https://en.wikipedia.org/wiki/Napoleon"
  python pipeline.py --url "https://en.wikipedia.org/wiki/Marie_Curie"
        """
    )
    
    parser.add_argument(
        '--url', 
        default="https://en.wikipedia.org/wiki/Alexander_the_Great",
        help="Wikipedia URL to process (default: Alexander the Great)"
    )
    
    args = parser.parse_args()
    
    # Validate URL
    if not args.url.startswith("https://en.wikipedia.org/wiki/"):
        print("❌ Error: URL must be a valid English Wikipedia article")
        print("   Format: https://en.wikipedia.org/wiki/Article_Name")
        return 1
    
    # Run the pipeline
    success = run_pipeline(args.url)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())