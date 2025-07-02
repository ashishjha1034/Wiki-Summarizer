# Wiki-Summarizer

## Overview
Wiki-Summarizer is a Python-based tool designed to generate concise summaries of Wikipedia articles using Natural Language Processing (NLP) techniques. This project leverages libraries such as BeautifulSoup for web scraping, NLTK for text processing, and Gensim for extractive text summarization, providing an efficient solution for summarizing lengthy Wikipedia content. The tool also includes keyword extraction based on entropy, making it ideal for users who need quick insights from Wikipedia articles.

## Features
- **Article Scraping**: Fetches content from Wikipedia articles using BeautifulSoup.
- **Extractive Summarization**: Generates concise summaries using Gensim’s summarization capabilities.
- **Keyword Extraction**: Identifies key terms based on entropy for enhanced content understanding.
- **Customizable Output**: Allows users to specify the length of summaries.
- **User-Friendly**: Simple command-line interface for easy interaction.

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Dependencies
The project requires the following Python libraries:
- `beautifulsoup4`
- `lxml`
- `nltk`
- `gensim`

Install the dependencies by running:
```bash
pip install -r requirements.txt
```

Additionally, you may need to download NLTK data:
```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/ashishjha1034/Wiki-Summarizer.git
   ```
2. Navigate to the project directory:
   ```bash
   cd Wiki-Summarizer
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the summarizer script:
   ```bash
   python summarizer.py
   ```
2. Enter the URL of the Wikipedia article when prompted (e.g., `https://en.wikipedia.org/wiki/Python_(programming_language)`).
3. The tool will scrape the article, process the text, and output a summary along with extracted keywords.

### Example
```bash
$ python summarizer.py
Which Wikipedia article would you want me to summarize: https://en.wikipedia.org/wiki/Python_(programming_language)
[Output]
Summary: Python is a high-level, interpreted programming language known for its readability and versatility. Created by Guido van Rossum in the late 1980s, it supports multiple programming paradigms and is widely used in web development, data science, and automation.
Keywords: Python, programming, Guido van Rossum, data science, web development
```

## Project Structure
- `summarizer.py`: Main script for scraping, summarizing, and keyword extraction.
- `requirements.txt`: List of required Python libraries.
- `README.md`: Project documentation (this file).

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

Please ensure your code follows the project's coding standards and includes appropriate documentation.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) for web scraping.
- [NLTK](https://www.nltk.org/) for text processing.
- [Gensim](https://radimrehurek.com/gensim/) for summarization and keyword extraction.

## Contact
For issues or suggestions, please open an issue on the [GitHub repository](https://github.com/ashishjha1034/Wiki-Summarizer) or contact the maintainer at [ashishjha1034@example.com](mailto:ashishjha1034@gmail.com).