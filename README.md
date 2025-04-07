# 🚀 ScrapeSmart - AI-Powered Web Scraper

**ScrapeSmart** is an advanced AI-driven web scraper that intelligently extracts, processes, and structures data from websites with minimal configuration. Built for developers, researchers, and data enthusiasts, it combines the power of AI with flexible scraping capabilities to deliver clean, organized data.

![ScrapeSmart Banner](https://via.placeholder.com/800x200?text=ScrapeSmart)

## ✨ Key Features

- 🤖 **AI-Powered Extraction** - Intelligently identifies and extracts relevant content using advanced language models
- 🔍 **Smart Crawling** - Navigate through multiple pages by following links with configurable depth limits
- 🧠 **Contextual Understanding** - Extract data that matches specific semantic criteria, not just pattern matching
- 📊 **Structured Output** - Automatically organizes scraped content into clean, structured formats
- 🖼️ **Media Support** - Extract images, store them locally, and maintain references in the output data
- 📤 **Versatile Export** - Save your data in multiple formats (JSON, CSV, Excel, plain text)
- 🎛️ **User-Friendly Interface** - Intuitive Streamlit-based UI for easy configuration and monitoring
- 🛡️ **Respectful Scraping** - Built-in rate limiting and user-agent rotation to respect website resources

## 🔧 Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/Maarij-Aqeel/ScrapeSmart.git
   cd ScrapeSmart
   ```

2. **Create and activate a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API Keys**
    
   Add your API keys to the `secrets.toml` file:
   ```toml
   GEMINI_API_KEY = "your_gemini_api_key_here"
   # Add other API keys as needed
   ```

## 📖 Usage Guide

### Starting the Application

Run the Streamlit application:
```bash
streamlit run app.py
```

This will launch ScrapeSmart in your default web browser.

### Basic Workflow

1. **Enter Target URL** - Specify the website URL you want to scrape in the sidebar
2. **Configure Options** - Select what to extract:
   - Text content
   - Images
   - Links
   - Custom elements
3. **Set Crawling Parameters** - Configure:
   - Crawling depth (how many links to follow)
   - Page limit
   - URL patterns to include/exclude
4. **Select AI Model** - Choose which model to use for processing
5. **Customize Extraction Prompt** - Fine-tune how the AI interprets the content
6. **Execute** - Click "Scrape and Extract" to begin the process
7. **Download** - Once complete, download the data in your preferred format

### Example Use Cases

- Extract product details from e-commerce websites
- Gather research papers and their abstracts from academic portals
- Compile news articles on specific topics
- Build datasets from web content for machine learning projects

## 🛠️ Advanced Customization

ScrapeSmart is designed to be easily customizable to fit your specific needs:

### Modifying Scraping Logic
Edit `scraper.py` to adjust how content is gathered:
```python
# Example: Adding custom selector support
def extract_with_custom_selector(self, selector):
    # Your custom extraction logic here
    pass
```

### Custom Data Processing
Extend `data_preprocessor.py` to implement specialized transformations:
```python
# Example: Adding a custom filter
def filter_content_by_relevance(self, content, threshold=0.5):
    # Your filtering logic here
    return filtered_content
```

### UI Customization
Modify `app.py` to change the interface or add new features:
```python
# Example: Adding a new configuration option
custom_option = st.sidebar.checkbox("Enable my custom feature")
if custom_option:
    # Custom feature implementation
    pass
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing
- [Streamlit](https://streamlit.io/) for the user interface

---
