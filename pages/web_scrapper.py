import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import pandas as pd
import time
from typing import Dict, List, Optional

class GenericConferenceScraper:
    """Generic scraper for conference websites with configurable patterns"""
    
    def __init__(self):
        """Initialize the scraper with Selenium WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Set up Chrome driver with options
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def __del__(self):
        """Clean up the WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

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

st.title("Conference Website Academic Scraper")

url = st.text_input("Enter conference website URL:")
wait_time = st.slider("Page load wait time (seconds)", 1, 15, 5)
min_confidence = st.slider("Minimum confidence score", 0.0, 1.0, 0.7)

if st.button("Extract Academic Information"):
    if url:
        with st.spinner("Initializing scraper..."):
            scraper = GenericConferenceScraper()
        
        with st.spinner("Scraping webpage..."):
            content = scraper.scrape_webpage(url, wait_time)
        
        if content:
            with st.spinner("Extracting academic information..."):
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
    else:
        st.warning("Please enter a URL.")
