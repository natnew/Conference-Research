"""
Web Scraper - Advanced Academic Website Extraction Tool
======================================================

A sophisticated Streamlit web scraping application for extracting academic profiles from
conference websites, institutional pages, and academic databases. Uses Selenium WebDriver
for dynamic content handling and AI-powered data extraction.

KEY FEATURES:
- Selenium WebDriver automation with cookie consent management
- AI-powered name/affiliation extraction using OpenAI models
- Beautiful Soup HTML parsing with Pydantic validation
- Excel export and intelligent wait strategies for dynamic content

REQUIREMENTS:
- openai_api_key: OpenAI API key
- Dependencies: streamlit, selenium, webdriver-manager, beautifulsoup4, pandas, pydantic, openai
- System: Chrome browser (auto-managed)

TECHNICAL ARCHITECTURE:
- Chrome WebDriver with headless mode and automated driver management
- Content pipeline: URL navigation → cookie handling → dynamic loading → HTML extraction
- AI analysis → data validation → structured formatting → export

WORKFLOW:
1. Input URL → 2. Configure parameters → 3. Navigate and handle popups
4. Wait for content → 5. Extract with Beautiful Soup → 6. AI analyzes content
7. Validate data → 8. Present results → 9. Export to Excel

USE CASES:
- Conference participant extraction and faculty directory scraping
- Academic event speaker collection and contact database building
- Research collaboration analysis and outreach list creation

COMPATIBILITY:
JavaScript-heavy sites, SPAs, GDPR consent sites, dynamic AJAX content
"""

import os
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from io import BytesIO

# Sidebar content
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A specialized web scraping tool designed to extract academic profiles from conference
websites and institutional pages. Automatically identifies and extracts names,
affiliations, and other relevant information while handling dynamic content and
cookie consents.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This scraper includes advanced capabilities:
    - Automated cookie consent handling
    - Dynamic content loading support
    - Smart name and affiliation detection
    - Customizable wait times and thresholds
    - Export results to Excel format
    """)

with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "Simply paste a URL from a conference website or academic page. "
        "The scraper will navigate through cookie notices, wait for content to load, "
        "and extract structured information about academics and their affiliations."
    )
    st.markdown(
        "This tool is continuously being improved to better handle various website layouts "
        "and data formats. Your feedback helps us enhance its capabilities."
    )

def get_chrome_driver():
    """
    Initializes and configures Chrome WebDriver with headless options optimized for Streamlit Cloud deployment.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance ready for web scraping
        
    Raises:
        WebDriverException: If Chrome/Chromium installation fails or driver cannot be initialized
        Exception: If ChromeDriverManager cannot download or install appropriate driver version
        
    Configuration:
        - Headless mode for server environments
        - JavaScript enabled for dynamic content
        - GPU disabled for performance in cloud environments
        - Sandbox disabled for containerized deployments
        
    Dependencies:
        - webdriver-manager for automatic driver management
        - selenium for browser automation
        
    Note:
        Automatically handles Chrome driver version management and installation.
        Optimized for Streamlit Cloud but works in local environments.
        Uses ChromeType.CHROMIUM for broader compatibility.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--enable-javascript')

    try:
        chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        webdriver_instance = webdriver.Chrome(service=chrome_service, options=chrome_options)
        return webdriver_instance
    except Exception as e:
        st.error(f"Failed to initialize Chrome driver: {str(e)}")
        return None

class AcademicInfo(BaseModel):
    name: str
    affiliation: str
    location: Optional[str] = Field(None, description="The location of the academic's affiliation.")

class ParticipantList(BaseModel):
    participant_details: Optional[List[AcademicInfo]] = Field(description="List of names, affiliations, and locations.")

class GenericConferenceScraper:
    """Generic scraper for conference websites with configurable patterns"""

    def __init__(self):
        """Initialize the scraper with cached Selenium WebDriver"""
        self.webdriver_instance = get_chrome_driver()
        if not self.webdriver_instance:
            st.error("Failed to initialize the scraper")
            st.stop()

    def __del__(self):
        """Clean up the WebDriver"""
        if hasattr(self, 'webdriver_instance') and self.webdriver_instance:
            try:
                self.webdriver_instance.quit()
            except:
                pass

    def handle_cookie_consent(self):
        """Handle cookie consent popups"""
        try:
            # Wait for cookie consent button (adjust selectors based on the actual page)
            cookie_buttons = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'accept')]",
                "//button[contains(@class, 'accept')]",
                "//button[contains(text(), 'Allow')]",
                "//button[contains(text(), 'Agree')]",
                # Add specific button for your site
                "//button[text()='Accept']"
            ]

            for button_xpath in cookie_buttons:
                try:
                    WebDriverWait(self.webdriver_instance, 5).until(
                        EC.element_to_be_clickable((By.XPATH, button_xpath))
                    ).click()
                    st.info("Cookie consent handled")
                    time.sleep(2)  # Wait for the popup to disappear
                    return True
                except (TimeoutException, ElementClickInterceptedException):
                    continue

            return False
        except Exception as e:
            st.warning(f"Cookie consent handling failed: {str(e)}")
            return False

    def wait_for_content(self, timeout=30):
        """Wait for dynamic content to load"""
        try:
            # Wait for specific elements that indicate content has loaded
            # Adjust these selectors based on the actual page structure
            content_indicators = [
                "//div[contains(@class, 'faculty')]",
                "//div[contains(@class, 'speakers')]",
                "//div[contains(@class, 'content')]"
            ]

            for indicator in content_indicators:
                try:
                    WebDriverWait(self.webdriver_instance, timeout).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    return True
                except TimeoutException:
                    continue

            return False
        except Exception as e:
            st.warning(f"Content loading wait failed: {str(e)}")
            return False

    def scrape_webpage(self, url: str, wait_time: int = 5) -> str:
        """Scrape webpage content with cookie handling and dynamic content waiting"""
        if not self.webdriver_instance:
            return ""

        try:
            st.info(f"Accessing URL: {url}")
            self.webdriver_instance.get(url)
            time.sleep(wait_time)  # Initial wait for page load

            # Handle cookie consent
            if self.handle_cookie_consent():
                st.info("Cookies accepted, waiting for content to load...")
            else:
                st.warning("Cookie consent not found or couldn't be handled")

            # Wait for dynamic content
            if self.wait_for_content():
                st.info("Content loaded successfully")
            else:
                st.warning("Content loading timeout - proceeding with available content")

            # Get the page source after all handling
            return self.webdriver_instance.page_source
        except Exception as e:
            st.error(f"Error accessing URL: {str(e)}")
            return ""

    def get_readable_text(self, content: str) -> str:
        """Extract readable text from HTML content"""
        soup = BeautifulSoup(content, 'html.parser')

        # Remove script and style elements
        for script in soup(['script', 'style']):
            script.decompose()

        # Get text and clean it up
        text = soup.get_text(separator='\n', strip=True)
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text

def extract_academic_info(text: str, openai_client: OpenAI) -> List[Dict[str, str]]:
    """
    Extracts structured academic information from unstructured text using OpenAI LLM processing.
    
    Args:
        text (str): Raw text content from web pages or documents containing academic information
        openai_client (OpenAI): Configured OpenAI client instance with valid API credentials
        
    Returns:
        Dict[str, List[Dict[str, str]]]: Parsed academic information with a
        ``participant_details`` key containing dictionaries with:
                            - ``name``: Full name of academic individual
                            - ``affiliation``: University or research institution
                            - ``location``: Country location inferred from affiliation
                            
    Raises:
        openai.OpenAIError: If API request fails, quota exceeded, or authentication fails
        
    Dependencies:
        - OpenAI GPT model for intelligent text analysis
        - Structured prompting for consistent academic information extraction
        
    Note:
        Designed for academic conference websites, faculty listings, and research directories.
        Uses intelligent parsing to handle various text formats and structures.
        Results may vary based on input text quality and formatting consistency.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract the names, affiliations, and locations from the following text and for location if not present "
                    "and based on the affiliations you can infer it from your general knowledge and just provide the country "
                    "name in the location and DON'T include the city name. Return the results as a JSON array of objects with "
                    "'name', 'affiliation', and 'location' keys."
                ),
            },
            {"role": "user", "content": text},
        ],
        response_model=ParticipantList,
    )

    parsed = response.parse()
    return parsed.model_dump()

def main():
    """
    Main execution function for the Web Scraper Streamlit application interface.
    
    Functionality:
        - Renders comprehensive Streamlit UI for web scraping configuration
        - Manages URL input, scraping parameters, and extraction settings
        - Coordinates between ConferenceScraper class and academic information extraction
        - Handles real-time progress indication and error reporting
        - Provides data export capabilities (CSV, Excel, JSON formats)
        - Manages session state for scraping results and configuration persistence
        
    Side Effects:
        - Updates Streamlit session state with scraping results and settings
        - Renders dynamic UI components based on scraping progress and results
        - Handles file downloads and data persistence operations
        - Manages WebDriver lifecycle and cleanup
        
    Features:
        - Real-time scraping progress with status indicators
        - Configurable wait times and scraping parameters
        - Academic information extraction with AI-powered analysis
        - Multiple export formats for different use cases
        - Error handling with user-friendly feedback
        
    Note:
        Entry point for the generic web scraping application.
        Designed for academic conference websites but adaptable to other structured sites.
        Includes comprehensive error handling for network issues, parsing failures, and API errors.
    """
    st.title("Web Scraper")

    url = st.text_input(
           "Enter website URL:",
           placeholder="e.g., https://example.com"
        )
    wait_time = st.slider(
        "Page Load Wait Time (seconds)",
        min_value=1,
        max_value=15,
        value=5,
        help="Adjust this slider to control how long the scraper waits for a webpage to load. If the website is slow or has complex dynamic content, increase this time to ensure all information is captured. A longer wait time helps with websites that load content gradually or have multiple loading stages."
    )

    st.caption(
        "Increase the wait time if the target page loads slowly or relies on dynamic content."
    )

    if st.button("Extract Information"):
        if url:
            try:
                with st.spinner("Initializing scraper..."):
                    scraper = GenericConferenceScraper()

                with st.spinner("Scraping webpage..."):
                    content = scraper.scrape_webpage(url, wait_time)

                if content:
                    # Extract and display readable text
                    with st.spinner("Processing raw text..."):
                        readable_text = scraper.get_readable_text(content)
                        st.subheader("Raw Scraped Text")
                        with st.expander("Click to view raw text", expanded=False):
                            st.text_area("", readable_text, height=300)

                    with st.spinner("Extracting information..."):
                        openai_client = OpenAI(api_key=st.secrets["openai_api_key"])
                        academics_dict = extract_academic_info(readable_text, openai_client)

                    if academics_dict:
                        academics_list = academics_dict.get("participant_details", [])
                        df = pd.DataFrame(academics_list)

                        st.subheader("Results")
                        st.dataframe(df)

                        # Save as Excel
                        output = BytesIO()
                        df.to_excel(output, index=False, engine='openpyxl')
                        output.seek(0)
                        st.download_button(
                            "Download Results as Excel",
                            output,
                            "conference_academics.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key='download-excel'
                        )
                    else:
                        st.warning("No academic information found. Try adjusting the wait time.")
                else:
                    st.error("Failed to retrieve content from the URL.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again with different parameters or check the URL.")
        else:
            st.warning("Please enter a URL.")

if __name__ == "__main__":
    main()
