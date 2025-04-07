"""
Web scraper module with core scraping functionality.

This module provides classes and functions for web scraping, content extraction,
and preprocessing of HTML content.
"""

from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
import time
import streamlit as st


class WebScraper:
    """Handles web scraping operations for extracting website content."""

    def __init__(self, arguments, driver_path, timeout=2):
        """Initializes a new WebScraper instance with Chrome WebDriver.

        Parameters:
            arguments (str): Command-line arguments to pass to the Chrome browser (typically user agent settings).
            driver_path (str): Path to the ChromeDriver executable.
            timeout (int, optional): Time in seconds to wait after loading a page before"""

        options = webdriver.ChromeOptions()
        options.add_argument(arguments)
        self.driver = webdriver.Chrome(service=Service(driver_path), options=options)
        self.timeout = timeout
        self.urls = ""
        self.html = ""

    def scrape(self, url):
        """Scrapes a single URL and extracts cleaned text content and links.

        Parameters:
            url (str): URL of the webpage to scrape.

        Returns:
            tuple: (str, set) Containing the cleaned text content and a set of extracted URLs."""
        try:
            self.driver.get(url)
            self.html = self.driver.page_source
            time.sleep(self.timeout)

        except Exception as e:
            return e

        soup = BeautifulSoup(self.html, "html.parser")
        body = soup.body
        if body:
            self.extracted_body = str(body)

            soup = BeautifulSoup(self.extracted_body, "html.parser")
            for script_style in soup(["script", "style"]):
                script_style.decompose()

            for a_tag in soup.find_all("a", href=True):
                a_tag.insert_after(f"[{a_tag['href']}]")

            cleaned = soup.get_text("\n")
            cleaned = "\n".join(
                line.strip() for line in cleaned.splitlines() if line.strip()
            )

            self.cleaned_result = cleaned
            urls = set()
            links = self.cleaned_result.splitlines()
            for link in links:
                if "https" in link.strip("[]") or "http" in link.strip("[]"):
                    urls.add(link.strip("[]"))

            self.urls = urls

        else:
            self.cleaned_result = ""
            self.urls = ""
        return (self.cleaned_result, self.urls)

    def extract_images(self, url, max_images):
        """Extracts image URLs from the previously scraped HTML content.

        Parameters:
            url (str): Base URL of the webpage (used for resolving relative image URLs).
            max_images (int): Maximum number of images to extract.

        """
        soup = BeautifulSoup(self.html,'html.parser')
        images = soup.find_all("img")

        image_urls = []
        for i, img in enumerate(images, start=1):
            src = img.get("src")

            if src:
                # Handle relative URLs
                if src.startswith("//"):
                    src = "https:" + src
                elif src.startswith("/"):
                    src = url.rstrip("/") + src
                elif not src.startswith(("http://", "https://")):
                    src = url.rstrip("/") + "/" + src

                image_urls.append(src)

            if i == max_images:
                break


        # st.session_state.image_urls = image_urls
        return image_urls

    def dom_content_length(self, content, max_length=6000):
        """splits content into chunks of specified maximum length.

        Parameters:
            content (str): Text content to split.
            max_length (int, optional): Maximum length of each chunk. Defaults to 6000.

        Returns:
            list: List of content chunks."""
        return [content[i : i + max_length] for i in range(0, len(content), max_length)]

    def Multi_scrape(self, start_url, adv_options, progress_bar):
        """Performs multi-page scraping starting from a given URL, with configurable options and progress tracking.

        Parameters:
            start_url (str): The initial URL to start scraping from.
            adv_options (dict): Dictionary of advanced scraping options including:
            max_urls (int): Maximum number of URLs to scrape.
            img (bool): Whether to extract images.
            max_images (int): Maximum number of images to extract per page.
            urls_scrape (bool): Whether to follow and scrape links found on pages.
            progress_bar: Streamlit progress bar object for displaying scraping progress.

        Returns:
            str: Combined cleaned text content from all scraped pages.
        """
        all_cleaned_text = ""
        visited_urls = set()
        urls_to_scrape = [start_url]
        scraped_count = 0

        status_text = st.empty()

        while urls_to_scrape and scraped_count < adv_options["max_urls"]:
            # Get the next URL to scrape
            current_url = urls_to_scrape.pop(0)

            if "cloudflare" in current_url:
                st.warning("⚠️CloudFlare protection detected, Stopping...")
                return all_cleaned_text

            # Skip if already visited or invalid
            if current_url in visited_urls or not current_url.startswith(
                ("http://", "https://")
            ):
                continue

            visited_urls.add(current_url)

            # Update status message
            status_text.write(
                f"**Scraping** website {scraped_count + 1}/{adv_options['max_urls']}: {current_url}"
            )

            try:
                # Perform scraping
                cleaned_text, links = self.scrape(current_url)
                st.session_state.urls = links

                # Add to the accumulated text
                all_cleaned_text += (
                    "\n\n" + cleaned_text if all_cleaned_text else cleaned_text
                )

                # Store the most recent content in session state
                st.session_state.dom_content = all_cleaned_text

                # Handle image extraction if enabled
                if adv_options["img"]:
                    st.session_state.image_urls = self.extract_images(
                        current_url, adv_options["max_images"]
                    )

                # Increment the counter
                scraped_count += 1

                # Update the progress bar
                progress_bar.progress(
                    scraped_count / adv_options["max_urls"],
                    text=f"Scraped {scraped_count}/{adv_options['max_urls']} pages",
                )

                # Extract additional URLs if enabled and we haven't reached the limit
                if (
                    adv_options["urls_scrape"]
                    and scraped_count < adv_options["max_urls"]
                ):
                    new_urls = list(links)

                    # Add new URLs to our queue if they haven't been visited
                    for url in new_urls:
                        if url not in visited_urls and url not in urls_to_scrape:
                            urls_to_scrape.append(url)

            except Exception as e:
                st.error(f"Error scraping website {current_url}: {e}")

        # Clear the status message when done
        status_text.empty()

        if not all_cleaned_text:
            st.warning("⚠️ No content was successfully scraped.")
        else:
            st.success(f"Finished scraping {scraped_count} pages.")

        self.cleaned_result = all_cleaned_text
        self.urls = st.session_state.urls
