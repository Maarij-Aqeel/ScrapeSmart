"""
Web scraping and AI extraction application main module.
This is the main application module for ScrapeSmart, a web-based tool for
scraping websites and extracting structured information using AI models.
"""

import os
import streamlit as st
from AI_model import Model
from scraper import WebScraper
from data_preprocessor import DataProcessor, FileManager
import random
import pandas as pd


class ScrapingConfig:
    """Configuration settings for the scraping process."""

    def __init__(
        self,
        max_images=None,
        chunking=False,
        extract_images=False,
        scrape_urls=False,
        max_urls=1,
        model="gemini-2.0-flash-lite",
    ):
        self.max_images = max_images
        self.chunking = chunking
        self.extract_images = extract_images
        self.scrape_urls = scrape_urls
        self.max_urls = max_urls
        self.model = model

    @staticmethod
    def load_api_key(keyname, provider_name):
        """
        Load or prompt for API key.

        Args:
            keyname: Name of the key in secrets
            provider_name: Display name of the API provider

        Returns:
            API key if available, otherwise None
        """
        api_key = None

        if keyname in st.secrets:
            api_key = st.secrets[keyname]
            st.success("API Key successfully loaded from secrets")
        else:
            api_key = st.text_input(
                f"🔑 Enter {provider_name} API Key", type="password"
            )
            try:
                if api_key:
                    # Create .streamlit directory if it doesn't exist
                    os.makedirs(".streamlit", exist_ok=True)

                    # Check if secrets.toml exists and append or create as needed
                    if os.path.exists(".streamlit/secrets.toml"):
                        with open(".streamlit/secrets.toml", "a") as api_file:
                            api_file.write(f"\n{keyname}='{api_key}'")
                    else:
                        with open(".streamlit/secrets.toml", "w") as api_file:
                            api_file.write(f"{keyname}='{api_key}'")

                    st.success("API Key set successfully!")
            except Exception as e:
                st.error(f"Error saving API key: {e}")

        return api_key


class ScrapeSmart:
    def __init__(self):
        """Initialize the ScrapeSmart application."""
        self.setup_page()
        self.config = None
        self.api_key = None
        self.web_scraper = WebScraper(
            arguments="--headless=new", driver_path="./chromedriver"
        )
        self.data_processor = DataProcessor()
        self.file_manager = FileManager()
        self.model = None

        # Initialize session state
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        if "scraped" not in st.session_state:
            st.session_state.scraped = 0

    def setup_page(self):
        """Configure the Streamlit page layout and style."""
        st.set_page_config(
            page_title="ScrapeSmart",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded",
            menu_items={"About": "https://github.com/Maarij-Aqeel"},
        )

        st.markdown(
            """
        <style>
            @keyframes fadeIn {
                from {opacity: 0;}
                to {opacity: 1;}
            }
            .stMarkdown, .stTextInput, .stButton, .stTextArea {
                animation: fadeIn 0.8s ease-in-out;
            }
            .title {
                font-size: 2.8em;
                font-weight: bold;
                text-align: center;
                color: #4A90E2;
                margin-bottom: 20px;
                padding: 10px;
                border-bottom: 2px solid #e0e0e0;
            }
            .stExpander {
                border: 1px solid #f0f0f0;
                border-radius: 8px;
                margin: 10px 0;
            }
            .stChatMessage {
                border-radius: 12px;
                margin: 8px 0;
            }
            .stAlert {
                border-radius: 8px;
            }
            
        </style>
        """,
            unsafe_allow_html=True,
        )

    def run(self):
        """Main entry point to run the application."""
        # Title
        st.markdown("<div class='title'>🌐 ScrapeSmart</div>", unsafe_allow_html=True)

        # Create layout
        col1, col2 = st.columns([2, 1])

        with col2:
            self.config = self.advanced_options()

        self.create_sidebar()

        # Initialize AI model
        self.model = Model(self.config.model, self.api_key)

        with col1:
            self.handle_scraping_process()

        self.handle_ai_extraction()
        # Footer
        self.display_footer()

    def advanced_options(self):
        """
        Provides advanced scraping configuration options through an expandable UI section.

        Returns:
            ScrapingConfig: Configuration object containing scraping settings
        """
        with st.expander("**Advanced Options**", expanded=False, icon="🕸️"):
            col1, col2 = st.columns(2)
            max_images = None
            max_urls = 1

            # Image Extraction Checkbox
            with col1:
                extract_image_urls = st.checkbox("Extract Images", key="img_url")
                scrape_urls = st.checkbox(
                    "Scrape Found URLs",
                    value=False,
                    help="Also scrape URLs found on the page",
                )
                chunking = st.checkbox(
                    "Use Text Chunking",
                    value=False,
                    help="Split large content into manageable chunks for AI processing",
                )
            with col2:
                if extract_image_urls:
                    max_images = st.number_input(
                        "Maximum Images", min_value=1, max_value=500, value=50
                    )

                if scrape_urls:
                    max_urls = st.number_input(
                        "Maximum URL's to scrape", min_value=2, max_value=500, value=10
                    )

        select_model = st.selectbox(
            ":blue[**Select AI Model**]",
            (
                "gemini-2.0-flash",
                "gemini-2.0-flash-lite",
                "gemini-1.5-flash",
                "gemini-1.5-flash-8b",
                "gemini-1.5-pro",
                "deepseek/deepseek-v3-base:free",
                "deepseek/deepseek-chat-v3-0324:free",
                "deepseek/deepseek-r1-zero:free",
            ),
            index=1,
            help="Select which AI model to use for extraction",
        )

        return ScrapingConfig(
            max_images,
            chunking,
            extract_image_urls,
            scrape_urls,
            max_urls,
            select_model,
        )

    def create_sidebar(self):
        """Create and configure the sidebar with input options."""
        with st.sidebar:
            st.title("⚙️ Configuration")

            # API Key Input based on model type
            if "gemini" in self.config.model:
                self.api_key = ScrapingConfig.load_api_key(
                    "GEMINI_API_KEY", "Google Gemini"
                )
            elif "deepseek" in self.config.model:
                self.api_key = ScrapingConfig.load_api_key(
                    "DEEPSEEK_API_KEY", "DeepSeek"
                )

            # Tutorial section
            st.markdown("""
                ## 📖 How to Use ScrapeSmart
                
                1. Enter a website URL in the sidebar
                2. Configure your extraction options
                3. Choose your preferred AI model
                4. Optionally customize the extraction prompt
                5. Click "Scrape and Extract" to start
                
                ## ✨ Features
                
                - **Web Scraping**: Extract text, images, and links from websites
                - **AI Analysis**: Use Google Gemini or DeepSeek to structure information
                - **Data Export**: Save extracted data in CSV, JSON, or Excel formats
                - **Customizable**: Configure extraction parameters and custom prompts
                
                ## 🚀 Getting Started
                
                Try scraping a product listing page, news article, or research publication to see how ScrapeSmart can extract structured information!
                """)

            st.divider()

    def handle_scraping_process(self):
        """Handle the website scraping process and display results."""
        # URL Input with descriptive placeholder
        url = st.text_input(
            "🌍 **Enter Website URL**",
            placeholder="https://example.com",
            help="Enter the full URL of the website you want to scrape",
        )

        # Initiate scraping process
        if st.button("**Scrape Website**", use_container_width=True):

            if "image_urls" in st.session_state:
                del st.session_state.image_urls
            if not url or not url.startswith(("http://", "https://")):
                st.warning(
                    "⚠️ Please enter a valid URL beginning with http:// or https://"
                )
            else:
                # Create a progress bar
                progress_bar = st.progress(0, text=":blue[**Starting to scrape...**]")

                # Convert config to dict for compatibility with existing WebScraper method
                config_dict = {
                    "max_images": self.config.max_images,
                    "chunking": self.config.chunking,
                    "img": self.config.extract_images,
                    "urls_scrape": self.config.scrape_urls,
                    "max_urls": self.config.max_urls,
                    "model": self.config.model,
                }

                # Call the scraping function with the progress bar
                self.web_scraper.Multi_scrape(url, config_dict, progress_bar)

        # Show scraped content if available
        if "dom_content" in st.session_state:
            self.display_scraping_results(url)

    def display_scraping_results(self, url):
        """Display the results of web scraping."""
        st.subheader("**Scraping Results**")
        tabs = st.tabs(
            [
                "**Scraped Content**",
                "**Extracted URLs**",
                "**Extracted Images URLs**",
            ]
        )

        if "url_editor_counter" not in st.session_state:
            st.session_state.url_editor_counter = 0
        else:
            st.session_state.url_editor_counter += 1

        with tabs[0]:
            with st.expander("**Extracted Content**"):
                st.text_area(label="", value=st.session_state.dom_content, height=300)

        urls = list(st.session_state.urls)
        df = pd.DataFrame(urls, columns=["Links"])
        with tabs[1]:
            with st.expander("URLs Dataset **(Editable)** "):
                st.data_editor(
                    df,
                    column_config={"Links": st.column_config.LinkColumn("Links")},
                    key=f"url_editor_{st.session_state.url_editor_counter}",
                )

        # Display image section if images were extracted
        if self.config.extract_images:
            with tabs[2]:
                self.display_images_section(url)
        else:
            with tabs[2]:
                st.info(
                    "To scrape images, enable 'Extract Images' in the advanced options"
                )

    def display_images_section(self, url):
        """Display and manage scraped images."""

        if "image_urls" not in st.session_state:
            st.session_state.image_urls=self.web_scraper.extract_images(url, self.config.max_images)

        # Save image URLs to a DataFrame
        image_df = pd.DataFrame(st.session_state.image_urls, columns=["Image URL"])
        
        # Add a counter in session state if it doesn't exist
        if "image_url_editor_counter" not in st.session_state:
            st.session_state.image_url_editor_counter = 0
        else:
            st.session_state.image_url_editor_counter += 1

        with st.expander("**Extracted Images URLs**"):
            st.data_editor(
                image_df,
                use_container_width=True,
                column_config={"Image URL": st.column_config.LinkColumn("URL")},
                key=f"image_url_editor_{st.session_state.image_url_editor_counter}",
            )

        # Initialize download state if not exists
        if "download_images" not in st.session_state:
            st.session_state.download_images = False

        # Use button to trigger download
        download_button = st.button("Download Images")

        # Update state when button changes
        if download_button != st.session_state.download_images:
            st.session_state.download_images = download_button

        # Execute the download when state is True
        if st.session_state.download_images:
            # Create images directory if it doesn't exist
            if not os.path.exists("images"):
                os.makedirs("images")
            st.session_state.Download_path = "./images/"

            self.file_manager.save_images(
                st.session_state.Download_path,
                st.session_state.image_urls,
                self.config.max_images,
            )
            st.success(
                f"**Total Images Downloaded:** {len(st.session_state.image_urls) if len(st.session_state.image_urls) < self.config.max_images else self.config.max_images} at {os.getcwd()}/{st.session_state.Download_path}"
            )

    def handle_ai_extraction(self):
        """Handle AI extraction from scraped content based on user input."""
        st.divider()
        st.subheader("🤖 AI Extraction")
        parse_description = st.chat_input("What do you want to extract? (Be specific)")

        # Initial greeting message
        if not parse_description:
            with st.chat_message("assistant"):
                st.markdown("**Hello**, How can I help you today?")

        # Display previous extraction results if available
        if "parsed_result" in st.session_state:
            with st.chat_message("user"):
                st.write(st.session_state.parsed_description)
            with st.chat_message("assistant"):
                st.markdown(st.session_state.parsed_result)

            if "df" in st.session_state:
                self.display_result_tabs()

        # Process new extraction request
        if parse_description:
            df = self.process_extraction_request(parse_description)

            if df is not None:
                st.session_state.df = df

                # Create filename from parsed description
                if "parsed_description" in st.session_state:
                    words = st.session_state.parsed_description.split()
                    file_name = random.choice(words) if words else "extraction_result"
                    st.session_state.file_name = file_name

                    if "parsed_result" in st.session_state:
                        self.display_result_tabs()

    def process_extraction_request(self, parse_description):
        """Process a user's extraction request with AI."""
        result = None

        # Handle case when no website has been scraped yet
        if "dom_content" not in st.session_state:
            with st.chat_message("user"):
                st.write(parse_description)

            with st.spinner("Processing your request..."):
                output, _ = self.model.process_with_nochunking("", parse_description)

            with st.chat_message("assistant"):
                st.markdown(output)
            return None

        # Validate API key
        if not self.api_key:
            st.warning("⚠️ Please enter a valid API Key")
            return None

        with st.chat_message("user"):
            st.write(parse_description)

        try:
            with st.chat_message("assistant"), st.spinner("Processing your request..."):
                chunks = self.web_scraper.dom_content_length(
                    st.session_state.dom_content
                )

                # Select appropriate parsing method based on model and chunking preference
                if self.config.chunking:
                    parsed_result, st.session_state["chat_history"] = (
                        self.model.process_with_chunking(
                            chunks, parse_description, st.session_state["chat_history"]
                        )
                    )
                else:
                    parsed_result, st.session_state["chat_history"] = (
                        self.model.process_with_nochunking(
                            chunks, parse_description, st.session_state["chat_history"]
                        )
                    )

                # Store parsed result in session state to persist it
                st.session_state.parsed_result = parsed_result
                st.session_state.parsed_description = parse_description

            st.success("Parsing complete!")

            # Process result to dataframe
            result = self.data_processor.Result_to_dataframe(
                st.session_state.parsed_result
            )
            return result

        except Exception as e:
            st.error(f"❌ Error during parsing: {e}")
            return None

    def display_result_tabs(self):
        """Display tabs with different formats of extraction results."""
        # Generate a unique timestamp for this specific rendering
        if "result_render_id" not in st.session_state:
            st.session_state.result_render_id = 0
        else:
            st.session_state.result_render_id += 1

        render_id = st.session_state.result_render_id

        result_tabs = st.tabs(
            ["**Plain Text**", "**CSV**", "**JSON**", "**HTML**", "**Excel**"]
        )

        with result_tabs[0]:
            with st.expander("**View**", expanded=False):
                st.write(st.session_state.parsed_result)
                self.file_manager.save_text(
                    st.session_state.parsed_result, st.session_state.file_name
                )

        with result_tabs[1]:
            with st.expander("**View**", expanded=False):
                # Use render_id to create a unique key
                if st.session_state.df.empty:
                    st.info("No Structured data founded")
                else:
                    st.data_editor(st.session_state.df, key=f"csv_editor_{render_id}")
                    self.file_manager.save_as(
                        st.session_state.df, "csv", st.session_state.file_name
                    )

        with result_tabs[2]:
            with st.expander("**View**", expanded=False):
                if st.session_state.df.empty:
                    st.info("No Structured data founded")
                else:
                    st.code(st.session_state.df.to_json())
                    self.file_manager.save_as(
                        st.session_state.df, "json", st.session_state.file_name
                    )

        with result_tabs[3]:
            with st.expander("**View**", expanded=False):
                if st.session_state.df.empty:
                    st.info("No Structured data founded")
                else:
                    st.code(st.session_state.df.to_html())
                    self.file_manager.save_as(
                        st.session_state.df, "html", st.session_state.file_name
                    )

        with result_tabs[4]:
            with st.expander("**View**", expanded=False):
                if st.session_state.df.empty:
                    st.info("No Structured data founded")
                else:
                    st.dataframe(st.session_state.df, key=f"excel_view_{render_id}")
                    self.file_manager.save_as(
                        st.session_state.df, "xlsx", st.session_state.file_name
                    )

    def display_footer(self):
        """Display the application footer."""
        st.markdown(
            """<div style='text-align:center; color:grey; padding:20px; margin-top:30px; border-top:2px solid #f0f0f0;'>
            ⚡ ScrapeSmart Powered by AI | <a href="https://github.com/Maarij-Aqeel/" target="_blank">Checkout my GitHub</a>
            </div>""",
            unsafe_allow_html=True,
        )


# Entry pointe
if __name__ == "__main__":
    app = ScrapeSmart()
    app.run()
