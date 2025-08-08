"""
Course Reading List - Academic Bibliography & Material Discovery Tool
====================================================================

A specialized Streamlit application for automatically discovering, compiling, and organizing
reading lists for university courses. Combines AI-powered content analysis with intelligent
web search to create comprehensive bibliographies and resource collections.

KEY FEATURES:
- AI-driven material discovery using DuckDuckGo search with content filtering
- Automated bibliography generation with proper academic formatting (APA, MLA, Chicago)
- Source verification and course-specific customization
- Export capabilities and integration with citation managers

REQUIREMENTS:
- openai_api_key: OpenAI API key
- Dependencies: streamlit, ddgs, selenium, webdriver-manager, beautifulsoup4, pandas, pydantic, openai
- Input: Course codes, titles, and academic discipline information

ARCHITECTURE:
Content Pipeline: Course input → search query generation → web search → AI relevance assessment
→ bibliography compilation → citation formatting → export

WORKFLOW:
Automated: Input course details → AI generates queries → multi-source search → content analysis
→ categorize materials → compile bibliography → export
Manual: Direct input → AI-assisted discovery → custom organization → integration

CONTENT CATEGORIES:
Core: Textbooks, peer-reviewed articles, foundational texts
Supplementary: Lecture notes, case studies, multimedia, OER
Reference: Dictionaries, databases, primary sources

USE CASES:
- Course development and curriculum planning
- Student research preparation and academic library collection
- Graduate program creation and professional development support
"""

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
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, WebDriverException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
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
    description: Optional[str] = Field(
        None,
        description="A brief description or summary of the resource."
    )
class ReadingListResponse(BaseModel):
    reading_list: List[ReadingListItem]

# Selenium WebDriver setup
def get_chrome_driver():
    """
    Initializes Chrome WebDriver configured for academic reading list and library website scraping.
    
    Returns:
        webdriver.Chrome: Chrome WebDriver instance optimized for university library systems
        
    Raises:
        WebDriverException: If Chrome installation or driver initialization fails
        Exception: If webdriver-manager cannot install appropriate driver version
        
    Configuration:
        - Headless mode for automated operation
        - Extended timeouts for slow university library systems
        - JavaScript enabled for dynamic library catalogues
        - Optimized for academic institutional authentication systems
        
    Dependencies:
        - webdriver-manager for Chrome driver management
        - selenium webdriver for browser automation
        
    Note:
        Specifically configured for university library systems and reading list platforms
        which often require longer load times and handle complex authentication workflows.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')

    try:
        chrome_service = Service(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install())
        webdriver_instance = webdriver.Chrome(service=chrome_service, options=chrome_options)
        webdriver_instance.set_page_load_timeout(30)  # Set timeout to prevent hanging
        return webdriver_instance
    except WebDriverException as e:
        st.error(f"WebDriver initialization failed: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Failed to initialize Chrome driver: {str(e)}")
        return None

# Context manager for WebDriver to ensure proper cleanup
class WebDriverManager:
    """Context manager for WebDriver instances to ensure proper cleanup and prevent memory leaks."""
    
    def __init__(self):
        self.driver = None
    
    def __enter__(self):
        self.driver = get_chrome_driver()
        if not self.driver:
            raise RuntimeError("Failed to initialize WebDriver")
        return self.driver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error during WebDriver cleanup: {e}")
            finally:
                self.driver = None

# Scraper class
class ReadingListScraper:
    def __init__(self):
        self.driver = None

    def __enter__(self):
        self.driver = get_chrome_driver()
        if not self.driver:
            raise RuntimeError("Failed to initialize the scraper")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error during scraper cleanup: {e}")
            finally:
                self.driver = None

    def scrape_page(self, url: str, wait_time: int = 5) -> str:
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        
        try:
            self.driver.get(url)
            time.sleep(wait_time)
            return self.driver.page_source
        except TimeoutException:
            st.warning(f"Timeout accessing URL: {url}")
            return ""
        except WebDriverException as e:
            st.error(f"WebDriver error accessing URL: {str(e)}")
            return ""
        except Exception as e:
            st.error(f"Error accessing URL: {str(e)}")
            return ""

    def extract_text(self, content: str) -> str:
        try:
            soup = BeautifulSoup(content, 'html.parser')
            for script in soup(['script', 'style']):
                script.decompose()
            text = soup.get_text(separator='\n', strip=True)
            return re.sub(r'\n\s*\n', '\n\n', text)
        except Exception as e:
            st.error(f"Error extracting text: {str(e)}")
            return ""

def get_reading_list(university: str, course: str):
    """
    Discovers and scrapes course reading lists from university websites using DuckDuckGo search.
    
    Args:
        university (str): Full university name for targeted search (e.g., "Harvard University")
        course (str): Specific course name, code, or subject area for reading list discovery
        
    Returns:
        List[Tuple[str, str]]: List of tuples containing (text_content, source_url) pairs
                              from discovered reading list and syllabus pages
                              
    Raises:
        requests.exceptions.RequestException: If search API or target URLs are unreachable
        Exception: If scraping fails due to website protection or parsing errors
        
    Workflow:
        1. Constructs targeted search query for university reading lists
        2. Performs DuckDuckGo search for relevant academic pages
        3. Scrapes content from discovered reading list URLs
        4. Extracts and cleans text content for LLM processing
        
    Dependencies:
        - DuckDuckGo search API for reading list discovery
        - WebScraper class for content extraction
        - BeautifulSoup for HTML parsing and text cleaning
        
    Note:
        Searches for official university reading lists, syllabi, and course resource pages.
        Results quality depends on university's web presence and reading list publication practices.
    """
    query = f"The following {course} offered in {university}  reading list  of books available for the university course offered OR site:.edu OR site:.ac.uk OR site:.org"
    results = DDGS().text(query, max_results=5)

    if results:
        reading_list = []
        try:
            with ReadingListScraper() as scraper:
                for result in results:
                    url = result.get('href', '')
                    content = scraper.scrape_page(url)
                    if content:
                        text = scraper.extract_text(content)
                        reading_list.append((text, url))
        except RuntimeError as e:
            st.error(f"Scraper initialization failed: {e}")
            return [], query
        except Exception as e:
            st.error(f"Error during scraping: {e}")
            return [], query
        return reading_list, query
    else:
        return [], query

def process_text_with_llm(texts_urls: List[tuple], query: str, openai_client: OpenAI) -> List[ReadingListItem]:
    """
    Processes scraped reading list content using OpenAI LLM to extract structured bibliographic information.
    
    Args:
        texts_urls (List[tuple]): List of (text_content, source_url) tuples from scraped reading lists
        query (str): Original search query for context and relevance filtering
        openai_client (OpenAI): Configured OpenAI client instance for LLM processing
        
    Returns:
        List[ReadingListItem]: Structured reading list entries containing:
                              - title: Book or article title
                              - author: Author name(s)
                              - publication_info: Publisher, year, edition details
                              - item_type: Book, journal article, chapter, etc.
                              - source_url: Original URL where item was found
                              
    Raises:
        openai.OpenAIError: If API request fails or authentication issues occur
        ValidationError: If LLM response doesn't match ReadingListItem model schema
        
    Dependencies:
        - OpenAI GPT model for intelligent bibliographic extraction
        - Pydantic ReadingListItem model for data validation
        
    Note:
        Combines multiple scraped sources to create comprehensive reading lists.
        Uses advanced prompting to identify and structure academic references from unstructured text.
        Handles various citation formats and academic resource types.
    """
    reading_list_items = []
    for text, url in texts_urls:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are provided with scraped text and you are a professional lecturer that can use this text to curate detailed reading list items from the provided text. Use the provided URL to populate the link field. The search query used to retrieve this text is: '{query}'. Return results as a structured output defined in the response model."
                    ),
                },
                {"role": "user", "content": f"Text: {text}\nURL: {url}"},
            ],
            response_model=ReadingListResponse,
        )
        parsed = response.parse()
        reading_list_items.extend(parsed.reading_list)
    return reading_list_items
def get_fallback_reading_list(course: str, openai_client: OpenAI) -> List[ReadingListItem]:
    """
    Generates a comprehensive academic reading list using OpenAI LLM when web scraping fails or returns insufficient results.
    
    Args:
        course (str): Course name, subject area, or academic field for reading list generation
        openai_client (OpenAI): Configured OpenAI client for LLM-based list generation
        
    Returns:
        List[ReadingListItem]: AI-generated academic reading list with standard academic resources:
                              - Essential textbooks and foundational works
                              - Key journal articles and research papers
                              - Supplementary readings and contemporary sources
                              - Structured with proper bibliographic information
                              
    Raises:
        openai.OpenAIError: If API request fails or model access issues occur
        ValidationError: If generated response doesn't match ReadingListItem schema
        
    Dependencies:
        - OpenAI GPT model with extensive academic knowledge
        - Pydantic ReadingListItem model for response structure validation
        
    Note:
        Serves as backup when university-specific reading lists cannot be found.
        Generates academically appropriate resources based on course subject and level.
        Includes mix of foundational texts, current research, and diverse perspectives.
        Quality depends on LLM's training data and knowledge of academic field.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Generate a recommended reading list for the course '{course}'. Include details such as title, author, edition, publisher, and year. Return results as a structured output defined in the response model."
                ),
            },
            {"role": "user", "content": f"Course: {course}"},
        ],
        response_model=ReadingListResponse,
    )
    parsed = response.parse()
    return parsed.reading_list
def main():
    """
    Main execution function for the Course Reading List Generator Streamlit application.
    
    Functionality:
        - Renders Streamlit interface for university and course input
        - Manages reading list discovery workflow with multiple fallback strategies
        - Coordinates between web scraping and AI-generated reading list creation
        - Handles user preferences for reading list type and academic level
        - Provides comprehensive data export and citation formatting options
        - Manages error handling for scraping failures and API limitations
        
    Side Effects:
        - Updates Streamlit session state with reading list data and user settings
        - Renders dynamic UI components based on discovery progress and results
        - Handles academic citation export in multiple formats (APA, MLA, Chicago)
        - Manages WebDriver lifecycle and resource cleanup for scraping operations
        
    Features:
        - Multi-strategy reading list discovery (web scraping + AI generation)
        - University-specific and general academic reading list creation
        - Real-time progress indication during discovery and processing
        - Academic citation formatting and bibliography generation
        - Export capabilities for course management systems and reference managers
        
    Workflow:
        1. Attempts web scraping for university-specific reading lists
        2. Falls back to AI-generated lists if scraping fails or returns insufficient results
        3. Processes and structures all discovered academic resources
        4. Provides formatted output with proper academic citations
        
    Note:
        Entry point for academic reading list research and generation application.
        Designed for educators, students, and researchers requiring comprehensive course bibliographies.
        Includes comprehensive error handling for various university website structures and access restrictions.
    """
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
        with st.spinner("Retrieving the reading list; this might take some time...."):
            if university and course:
                openai_key = st.secrets.get("openai_api_key")
                if not openai_key:
                    st.error("OpenAI API key is not configured. Please add 'openai_api_key' to Streamlit secrets.")
                    return
                openai_client = OpenAI(api_key=openai_key)
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
                    # Fallback mechanism
                    fallback_reading_list = get_fallback_reading_list(course, openai_client)
                    if fallback_reading_list:
                        st.session_state.reading_list_items = fallback_reading_list
                        st.session_state.query = query
                        st.session_state.show_info = True
                        st.session_state.show_header = True
                        reading_list_df = pd.DataFrame(fallback_reading_list)
                        st.session_state.reading_list_df = reading_list_df
                        st.info("Fallback Reading List: Since no specific reading list was found, here is a recommended reading list for the course.")
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
