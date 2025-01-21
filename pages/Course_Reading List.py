import streamlit as st
from duckduckgo_search import DDGS
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
import json
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from openai import OpenAI

# Sidebar content
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A dedicated tool to help students and educators retrieve and summarize reading lists for
university courses. The tool combines AI and web search to provide comprehensive
information on books, articles, and lecture materials related to specific courses.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This tool provides the following advanced capabilities:
    - AI-driven retrieval of books, articles, and lecture materials
    - User-friendly interface for customized queries
    - Support for fetching course-specific reading lists with source links
    - Efficient use of DuckDuckGo for search results
    """)

with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "This application enables users to access detailed reading lists for university courses. "
        "It retrieves books, articles, and lecture materials using AI and web search. "
        "The tool is ideal for educators, students, and researchers looking for quick access to structured "
        "course reading materials and sources."
    )
    st.markdown(
        "The tool is continuously improved to enhance its search accuracy and relevance. "
        "Your feedback helps us deliver better results."
    )

# Pydantic models
class ReadingListItem(BaseModel):
    title: str = Field(
        ...,
        description="The title of the resource (e.g., book, article, or lecture notes)."
    )
    author: Optional[str] = Field(
        None,
        description="The author of the resource, if applicable."
    )
    edition: Optional[str] = Field(
        None,
        description="The edition of the resource, if applicable."
    )
    publisher: Optional[str] = Field(
        None,
        description="The publisher of the resource, if applicable."
    )
    year: Optional[str] = Field(
        None,
        description="The year of publication or release of the resource."
    )
    link: Optional[str] = Field(
        None,
        description="A URL link to access the resource, if available."
    )
    description: Optional[str] = Field(
        None,
        description="A brief description or summary of the resource."
    )
    citation: Optional[str] = Field(
        None,
        description="A formatted citation for the resource."
    )
    doi: Optional[str] = Field(
        None,
        description="The Digital Object Identifier (DOI) for the resource, if applicable."
    )
    key_takeaways: Optional[str] = Field(
        None,
        description="A brief detailed overview and insights of the  resource."
    )
    resource_type: str = Field(
        ...,
        description="The type of resource (e.g., 'Book', 'Article', 'Lecture Notes')."
    )

class ReadingListResponse(BaseModel):
    reading_list: List[ReadingListItem]

# Selenium WebDriver setup
def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    try:
        service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        st.error(f"Failed to initialize Chrome driver: {str(e)}")
        return None

# Scraper class
class ReadingListScraper:
    def __init__(self):
        self.driver = get_chrome_driver()
        if not self.driver:
            st.error("Failed to initialize the scraper")
            st.stop()

    def __del__(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def scrape_page(self, url: str, wait_time: int = 5) -> str:
        try:
            self.driver.get(url)
            time.sleep(wait_time)
            return self.driver.page_source
        except Exception as e:
            st.error(f"Error accessing URL: {str(e)}")
            return ""

    def extract_text(self, content: str) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup(['script', 'style']):
            script.decompose()
        text = soup.get_text(separator='\n', strip=True)
        return re.sub(r'\n\s*\n', '\n\n', text)

# Function to fetch the reading list using DuckDuckGo
def get_reading_list(university: str, course: str):
    query = f"The following {course} offered in {university} reading list OR course materials OR syllabus site:.edu OR site:.ac.uk OR site:.org"
    results = DDGS().text(query, max_results=5)

    if results:
        reading_list = []
        scraper = ReadingListScraper()
        for result in results:
            url = result.get('href', '')
            content = scraper.scrape_page(url)
            if content:
                text = scraper.extract_text(content)
                reading_list.append((text, url))
        return reading_list, query
    else:
        return [], query

# Function to process text with LLM
def process_text_with_llm(texts_urls: List[tuple], query: str, openai_client: OpenAI) -> List[ReadingListItem]:
    reading_list_items = []
    for text, url in texts_urls:
        response = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": f"You are provided with scraped text and you are a professional lecturer that can use this text to curate detailed reading list items from the provided text. Use the provided URL to populate the link field. The search query used to retrieve this text is: '{query}'. Return results as a structured output defined in the response model."},
                {"role": "user", "content": f"Text: {text}\nURL: {url}"}
            ],
            response_format=ReadingListResponse
        )
        reading_list_data = response.choices[0].message.content
        reading_list_data_parsed = json.loads(reading_list_data)
        reading_list_items.extend(reading_list_data_parsed.get("reading_list", []))
    return reading_list_items

def main():
    st.title("Course Reading List")

    # Initialize session state
    if 'reading_list_items' not in st.session_state:
        st.session_state.reading_list_items = []
    if 'query' not in st.session_state:
        st.session_state.query = ""
    if 'reading_list_df' not in st.session_state:
        st.session_state.reading_list_df = pd.DataFrame()
    if 'show_info' not in st.session_state:
        st.session_state.show_info = False
    if 'show_header' not in st.session_state:
        st.session_state.show_header = False
    # University name Input Text Field
    university = st.text_input(
        "University Name",
        placeholder="e.g., Harvard Law School"
    )
    # Course Name Input text field
    course = st.text_input(
        "Course Name",
        placeholder="e.g., Criminal Law"
    )

    if st.button("Get Reading List"):
        with st.spinner("Fetching reading list might take while😉..."):
            if university and course:
                openai_client = OpenAI(api_key=st.secrets["openai_api_key"])
                texts_urls, query = get_reading_list(university, course)
                if texts_urls:
                    reading_list_items = process_text_with_llm(texts_urls, query, openai_client)
                    if reading_list_items:
                        st.session_state.reading_list_items = reading_list_items
                        st.session_state.query = query
                        st.session_state.show_info = True
                        st.session_state.show_header = True
                        reading_list_df = pd.DataFrame(reading_list_items)
                        st.session_state.reading_list_df = reading_list_df
                    else:
                        st.warning("No relevant reading list items found.")
                else:
                    st.warning("No results found. Please try a different query.")
            else:
                st.warning("Please provide both the University Name and Course Name.")

     # Display the informational message if it exists in the session state
    if st.session_state.show_info:
        st.info("Information Source: The information is retrieved from DuckDuckGo searches, which includes publicly available resources.")

    # Display the section header if it exists in the session state
    if st.session_state.show_header:
        st.write("### Reading List with recommended supporting materials")
    # Display the DataFrame if it exists in the session state
    if not st.session_state.reading_list_df.empty:
        st.dataframe(st.session_state.reading_list_df)
        # Export the results as a CSV
        csv = st.session_state.reading_list_df.to_csv(index=False)
        st.download_button(
            label="Export the Reading List as CSV",
            data=csv,
            file_name="reading_list.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
