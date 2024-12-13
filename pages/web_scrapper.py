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
import re
import pandas as pd
import time
from typing import Dict, List
import json
from groq import Groq

# Get API key from secrets
groq_api_key = st.secrets["groq_api_key"]

st.snow()

# Sidebar content
st.sidebar.title(":streamlit: Conference Research Assistant")
st.sidebar.write("""
A specialized web scraping tool designed to extract academic profiles from conference 
websites and institutional pages using LLM-powered extraction.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This scraper includes advanced capabilities:
    - LLM-powered name and affiliation extraction
    - Automated cookie consent handling
    - Dynamic content loading support
    - Export results to CSV format
    """)

def get_chrome_driver():
    """Initialize  the Chrome WebDriver with proper options for Streamlit Cloud"""
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
    def __init__(self):
        """Initialize the scraper with cached Selenium WebDriver and Groq client"""
        self.driver = get_chrome_driver()
        self.groq_client = Groq(api_key=groq_api_key)
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

    def handle_cookie_consent(self):
        """Handle cookie consent popups"""
        try:
            cookie_buttons = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'accept')]",
                "//button[contains(@class, 'accept')]",
                "//button[contains(text(), 'Allow')]",
                "//button[contains(text(), 'Agree')]",
                "//button[text()='Accept']"
            ]
            
            for button_xpath in cookie_buttons:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, button_xpath))
                    ).click()
                    st.info("Cookie consent handled")
                    time.sleep(2)
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

    def extract_academics_with_llm(self, text: str) -> List[Dict[str, str]]:
        """Extract academic information using Groq LLM"""
        prompt = f"""
        Extract names and affiliations of academics from the following text. 
        Return the results as a JSON array where each object has 'name' and 'affiliation' keys.
        Only include entries where you are confident about both the name and affiliation.
        
        Text to analyze:
        {text}
        
        Expected format:
        [
            {{"name": "John Smith", "affiliation": "Stanford University"}},
            {{"name": "Jane Doe", "affiliation": "MIT"}}
        ]
        """
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts structured information about academics from text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result = completion.choices[0].message.content
            try:
                academics = json.loads(result)
                return academics
            except json.JSONDecodeError:
                st.error("Failed to parse LLM response as JSON")
                return []
                
        except Exception as e:
            st.error(f"Error calling Groq API: {str(e)}")
            return []

    def scrape_webpage(self, url: str, wait_time: int = 5) -> str:
        """Scrape webpage content with cookie handling and dynamic content waiting"""
        if not self.driver:
            return ""

        try:
            st.info(f"Accessing URL: {url}")
            self.driver.get(url)
            time.sleep(wait_time)

            if self.handle_cookie_consent():
                st.info("Cookies accepted, waiting for content to load...")
            else:
                st.warning("Cookie consent not found or couldn't be handled")

            if self.wait_for_content():
                st.info("Content loaded successfully")
            else:
                st.warning("Content loading timeout - proceeding with available content")

            return self.driver.page_source
        except Exception as e:
            st.error(f"Error accessing URL: {str(e)}")
            return ""

    def get_readable_text(self, content: str) -> str:
        """Extract readable text from HTML content"""
        soup = BeautifulSoup(content, 'html.parser')
        
        for script in soup(['script', 'style']):
            script.decompose()
            
        text = soup.get_text(separator='\n', strip=True)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        return text

def main():
    st.title("Academic Information Extractor")

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
                    with st.spinner("Processing raw text..."):
                        readable_text = scraper.get_readable_text(content)
                        st.subheader("Raw Scraped Text")
                        with st.expander("Click to view raw text", expanded=False):
                            st.text_area("", readable_text, height=300)

                    with st.spinner("Extracting information using LLM..."):
                        academics = scraper.extract_academics_with_llm(readable_text)

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
                        st.warning("No academic information found. The LLM might need adjustments or the content might not contain the expected information.")
                else:
                    st.error("Failed to retrieve content from the URL.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again with different parameters or check the URL.")
        else:
            st.warning("Please enter a URL.")

if __name__ == "__main__":
    main()
