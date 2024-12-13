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
from typing import Dict, List, Optional
from groq import Groq

st.snow()

# Sidebar content
st.sidebar.title(":streamlit: Conference Research Assistant")
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
    - Export results to CSV format
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
    """Initialize the Chrome WebDriver with proper options for Streamlit Cloud"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--enable-javascript')

    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Failed to initialize Chrome driver: {str(e)}")
        return None

class GenericConferenceScraper:
    """Generic scraper for conference websites with configurable patterns"""

    def __init__(self):
        """Initialize the scraper with cached Selenium WebDriver"""
        self.driver = get_chrome_driver()
        if not self.driver:
            st.error("Failed to initialize the scraper")
            st.stop()
        self.groq_client = Groq(api_key=st.secrets["groq_api_key"])

    def __del__(self):
        """Clean up the WebDriver"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
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
                    WebDriverWait(self.driver, 5).until(
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
                    WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.XPATH, indicator))
                    )
                    return True
                except TimeoutException:
                    continue

            return False
        except Exception as e:
            st.warning(f"Content loading wait failed: {str(e)}")
            return False

    def extract_name_affiliation(self, text: str) -> Optional[Dict[str, str]]:
        """Extract name and affiliation from text using Groq LLM"""
        response = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Extract the name and affiliation from the following text: {text}"
                }
            ],
            model="llama-3.3-70b-versatile",
        )

        result = response.choices[0].message.content
        try:
            name, affiliation = result.split(',')
            return {
                'name': name.strip(),
                'affiliation': affiliation.strip()
            }
        except ValueError:
            return None

    def scrape_webpage(self, url: str, wait_time: int = 5) -> str:
        """Scrape webpage content with cookie handling and dynamic content waiting"""
        if not self.driver:
            return ""

        try:
            st.info(f"Accessing URL: {url}")
            self.driver.get(url)
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
            return self.driver.page_source
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

    def find_academics(self, content: str) -> List[Dict[str, str]]:
        """Find academic information in content"""
        soup = BeautifulSoup(content, 'html.parser')
        academics = []

        elements = soup.find_all(['p', 'div', 'span', 'td', 'li'])

        for element in elements:
            text = element.get_text(strip=True)
            if not text or len(text) < 10:
                continue

            result = self.extract_name_affiliation(text)
            if result:
                academics.append(result)

        return academics

def main():
    st.title("Web Scraper")

    url = st.text_input("Enter website URL:")
    wait_time = st.slider("Page load wait time (seconds)", 1, 15, 5)

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
                        academics = scraper.find_academics(content)

                    if academics:
                        df = pd.DataFrame(academics)
                        st.success(f"Found {len(academics)} academics!")

                        st.subheader("Results")
                        st.dataframe(df)

                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            "Download Results as CSV",
                            csv,
                            "conference_academics.csv",
                            "text/csv",
                            key='download-csv'
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
