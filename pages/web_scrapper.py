import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from typing import Dict, List, Optional

st.snow()


def get_chrome_driver():
    """Initialize  the Chrome WebDriver with proper options for Streamlit Cloud"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')

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

    def __del__(self):
        """Clean up the WebDriver"""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass

    @staticmethod
    def is_likely_name(text: str) -> bool:
        """Check if text looks like a person's name"""
        titles = r'(?:Dr\.|Prof\.|Mr\.|Mrs\.|Ms\.|PhD|MD|MA|BSc|MSc)'
        name_pattern = rf'^(?:{titles}\s*)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+'
        return bool(re.match(name_pattern, text))

    @staticmethod
    def is_likely_affiliation(text: str) -> bool:
        """Check if text looks like an institutional affiliation"""
        institution_keywords = [
            'University', 'College', 'Institute', 'School',
            'Department', 'Lab', 'Laboratory', 'Center', 'Centre',
            'Faculty', 'Academia', 'Research'
        ]
        return any(keyword.lower() in text.lower() for keyword in institution_keywords)

    def extract_name_affiliation(self, text: str) -> Optional[Dict[str, str]]:
        """Extract name and affiliation from text using various patterns"""
        patterns = [
            r'^(.*?),\s*(.*?)$',
            r'^(.*?)\s*\((.*?)\)$',
            r'^(.*?)\s+(?:at|from)\s+(.*?)$',
            r'^(.*?)\s*[-–]\s*(.*?)$',
        ]

        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                name, affiliation = match.groups()
                if (self.is_likely_name(name) and
                    self.is_likely_affiliation(affiliation)):
                    return {
                        'name': name.strip(),
                        'affiliation': affiliation.strip()
                    }
        return None

    def scrape_webpage(self, url: str, wait_time: int = 5) -> str:
        """Scrape webpage content with configurable wait time"""
        if not self.driver:
            return ""

        try:
            st.info(f"Accessing URL: {url}")
            self.driver.get(url)
            time.sleep(wait_time)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

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

    def find_academics(self, content: str, min_confidence: float = 0.7) -> List[Dict[str, str]]:
        """Find academic information in content with confidence scoring"""
        soup = BeautifulSoup(content, 'html.parser')
        academics = []

        elements = soup.find_all(['p', 'div', 'span', 'td', 'li'])

        for element in elements:
            text = element.get_text(strip=True)
            if not text or len(text) < 10:
                continue

            result = self.extract_name_affiliation(text)
            if result:
                confidence = 0.0
                name = result['name']
                affiliation = result['affiliation']

                if self.is_likely_name(name):
                    confidence += 0.5
                if self.is_likely_affiliation(affiliation):
                    confidence += 0.5

                if confidence >= min_confidence:
                    academics.append(result)

        return academics

def main():
    st.title("Web Scraper")

    url = st.text_input("Enter website URL:")
    wait_time = st.slider("Page load wait time (seconds)", 1, 15, 5)
    min_confidence = st.slider("Minimum confidence score", 0.0, 1.0, 0.7)

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
                        academics = scraper.find_academics(content, min_confidence)

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
                        st.warning("No academic information found. Try adjusting the confidence threshold or wait time.")
                else:
                    st.error("Failed to retrieve content from the URL.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again with different parameters or check the URL.")
        else:
            st.warning("Please enter a URL.")

if __name__ == "__main__":
    main()
