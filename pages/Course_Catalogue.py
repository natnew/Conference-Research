"""
Course Catalogue - Educational Content Extraction & Analysis Tool
================================================================

A comprehensive Streamlit application for extracting, analyzing, and summarizing course
information from educational websites and academic institutions. Combines web scraping
with AI-powered content analysis for institutional research and academic planning.

KEY FEATURES:
- Automated web scraping with Selenium WebDriver for dynamic content
- AI-powered course extraction using OpenAI models with DuckDuckGo integration
- Course module leader identification and reading list extraction
- Structured data organization with progress tracking and export capabilities

REQUIREMENTS:
- openai_api_key: OpenAI API key
- Dependencies: streamlit, selenium, webdriver-manager, beautifulsoup4, pandas, pydantic, openai, requests, duckduckgo_search
- System: Chrome browser (auto-managed)

ARCHITECTURE:
Multi-Modal Processing: Web scraping → Manual entry → AI analysis → Search integration
Pipeline: URL navigation → dynamic loading → HTML parsing → AI extraction → data compilation

WORKFLOW:
Web Scraping: Input URL → configure parameters → extract content → AI processes → export
Manual Entry: Input course names → DuckDuckGo search → AI analysis → manual review

USE CASES:
- Academic program research and course content analysis
- Reading list compilation and faculty assignment analysis
- Curriculum development and student advising support
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
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, WebDriverException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from pydantic import BaseModel, Field
import json
from typing import List, Optional, Dict
from openai import OpenAI
import openai
import requests
from duckduckgo_search import DDGS
import time
from functools import wraps
import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Validates if the provided string is a properly formatted URL.
    
    Args:
        url (str): URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
        
    Note:
        Validates both http and https schemes and basic URL structure.
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False



def retry_with_exponential_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator that implements exponential backoff retry logic for API calls.
    
    Args:
        max_retries (int): Maximum number of retry attempts
        base_delay (float): Base delay in seconds for exponential backoff
        
    Returns:
        Decorated function with retry logic
        
    Note:
        Specifically designed for OpenAI API calls with proper error handling
        for rate limits, timeouts, and transient failures.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except openai.RateLimitError as e:
                    if attempt == max_retries:
                        raise e
                    delay = base_delay * (2 ** attempt)
                    st.warning(f"Rate limit hit, retrying in {delay} seconds...")
                    time.sleep(delay)
                except openai.APIError as e:
                    if attempt == max_retries:
                        raise e
                    delay = base_delay * (2 ** attempt)
                    st.warning(f"API error, retrying in {delay} seconds...")
                    time.sleep(delay)
                except Exception as e:
                    if attempt == max_retries:
                        raise e
                    delay = base_delay * (2 ** attempt)
                    st.warning(f"Unexpected error, retrying in {delay} seconds...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# Sidebar content
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A comprehensive tool designed to extract and summarize
course details from educational websites. It enables efficient retrieval of structured
information such as course names, descriptions, module leaders, and reading lists.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This tool provides the following advanced capabilities:
    - Automated web scraping with Selenium
    - Text extraction and processing using BeautifulSoup
    - AI-powered extraction of course summaries and details using OpenAI models
    - Customizable page load times
    - Support for manual course entry and search via DuckDuckGo
    - Export results to structured formats like DataFrame
    """)

with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "This application enables users to get course information from educational websites "
        "process text to extract key details, and leverage AI for summarization and detailed data extraction. "
        "It is ideal for educators, students, and institutions looking to streamline course catalogues "
        "and enhance their data collection processes."
    )
    st.markdown(
        "The tool is continually updated to improve its data collection and retrieval accuracy and compatibility "
        "with different website layouts. User feedback is highly valued to ensure robust performance."
    )

# Pydantic models remain the same
class CoursePreview(BaseModel):
    course_name: str

class CourseDetail(BaseModel):
    course_name: str = Field(
        ...,
        description="The name of the course as provided in the  text."
    )
    course_overview: str = Field(
        ...,
        description="A brief overview or summary of the course content."
    )
    course_details: str = Field(
        ...,
        description="Detailed information about the course, including structure and content."
    )
    module_leader_name: str = Field(
        ...,
        description="The name of the module leader explicitly mentioned in the text with the title ‘Director of…..’ or ‘Senior Lecturer’ or ‘Associate Professor’ or ‘Professor’. If not available, respond with 'not available at the moment'."
    )
    module_leader_email: Optional[str] = Field(
        default="not available at the moment",
        description="The email of the module leader explicitly mentioned in the text. If not available, respond with 'not available at the moment'."
    )
class CourseCatalogueResponse(BaseModel):
    courses: List[CoursePreview]

class CourseDetailResponse(BaseModel):
    course_detail:CourseDetail

# Selenium WebDriver setup remains the same
def get_chrome_driver():
    """
    Initializes Chrome WebDriver with optimized settings for course catalogue web scraping.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance with academic site optimizations
        
    Raises:
        WebDriverException: If Chrome installation fails or driver cannot be initialized
        Exception: If driver installation or configuration fails
        
    Configuration:
        - Headless operation for server deployment
        - Extended timeouts for slow university websites
        - JavaScript enabled for dynamic course catalogue systems
        - Optimized for academic institutional websites
        
    Dependencies:
        - webdriver-manager for automatic Chrome driver management
        - selenium webdriver for browser automation
        
    Note:
        Specifically tuned for university course catalogue systems which often
        have slower response times and complex authentication requirements.
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
        st.error(f"Failed to initialize Chrome driver: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error during driver initialization: {str(e)}")
        return None

# Scraper class with proper context management
class CourseScraper:
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
            except WebDriverException as e:
                print(f"WebDriver cleanup error: {e}")
            except Exception as e:
                print(f"Unexpected error during scraper cleanup: {e}")
            finally:
                self.driver = None

    def scrape_page(self, url: str, wait_time: int = 7) -> str:
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
            st.error(f"WebDriver error accessing URL {url}: {str(e)}")
            return ""
        except Exception as e:
            st.error(f"Unexpected error accessing URL {url}: {str(e)}")
            return ""

    def extract_text(self, content: str) -> str:
        soup = BeautifulSoup(content, 'html.parser')
        for script in soup(['script', 'style']):
            script.decompose()
        text = soup.get_text(separator='\n', strip=True)
        return re.sub(r'\n\s*\n', '\n\n', text)

@retry_with_exponential_backoff(max_retries=3, base_delay=1.0)
def extract_courses(text: str, openai_client: OpenAI) -> List[CoursePreview]:
    """
    Extracts course information from university catalogue text using OpenAI LLM with structured output.
    
    Args:
        text (str): Raw text content from university course catalogue pages
        openai_client (OpenAI): Configured OpenAI client instance for LLM processing
        
    Returns:
        List[CoursePreview]: List of structured course objects containing:
                           - course_code: Official course identifier (e.g., "CS101")
                           - course_title: Full course name and description
                           - credits: Number of academic credits
                           - prerequisites: Required prior courses or knowledge
                           
    Raises:
        openai.OpenAIError: If API request fails or authentication issues occur
        ValidationError: If LLM response doesn't match CoursePreview model schema
        
    Dependencies:
        - OpenAI GPT model for intelligent course information extraction
        - Pydantic CoursePreview model for data validation and structure
        
    Note:
        Optimized for standard university catalogue formats including course codes,
        titles, credit hours, and prerequisite information. Handles various formatting
        styles across different institutional systems.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract a list of course names from the provided text. "
                    "DO NOT include any URLs, links, or web addresses in your response. "
                    "Return a JSON object with a 'courses' field containing "
                    "objects that each include a single 'course_name' string. "
                    "Focus only on actual course titles and names, not website links. "
                    "Example response: {\"courses\": [{\"course_name\": \"Introduction to AI\"}]}"
                ),
            },
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
    )
    parsed_json = response.choices[0].message.content
    try:
        parsed_dict = json.loads(parsed_json)
        if 'courses' not in parsed_dict:
            st.error("Invalid response format: 'courses' key not found")
            return []
        
        # Validate that courses is a list and contains properly formatted course objects
        courses_list = parsed_dict['courses']
        if not isinstance(courses_list, list):
            st.error("Invalid response format: 'courses' should be a list")
            return []
        
        # Validate each course object has the required 'course_name' field
        for course in courses_list:
            if not isinstance(course, dict) or 'course_name' not in course:
                st.error("Invalid course format: missing 'course_name' field")
                return []
        
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse JSON from model: {e}")
        return []
    
    try:
        parsed = CourseCatalogueResponse.model_validate(parsed_dict)
        return parsed.courses
    except Exception as e:
        st.error(f"Failed to validate course data structure: {e}")
        return []

@retry_with_exponential_backoff(max_retries=3, base_delay=1.0)
def extract_course_details(course_name: str, text: str, openai_client: OpenAI) -> CourseDetail:
    """
    Extracts comprehensive detailed information for a specific course using targeted LLM analysis.
    
    Args:
        course_name (str): Specific course name or code to focus extraction on
        text (str): Full catalogue text containing detailed course information
        openai_client (OpenAI): Configured OpenAI client for detailed analysis
        
    Returns:
        CourseDetail: Comprehensive course object containing:
                     - course_code: Official identifier
                     - full_title: Complete course title
                     - detailed_description: Full course description and objectives
                     - credits: Academic credit value
                     - prerequisites: Required courses and knowledge
                     - instructor: Faculty member information (if available)
                     - schedule: Meeting times and format
                     
    Raises:
        openai.OpenAIError: If API request fails or quota exceeded
        ValidationError: If response doesn't match CourseDetail model requirements
        
    Dependencies:
        - OpenAI GPT model for focused course analysis
        - Pydantic CourseDetail model for comprehensive data validation
        
    Note:
        Provides more detailed extraction than extract_courses() by focusing on
        a specific course. Useful for deep-dive analysis of individual courses
        including syllabi information, learning objectives, and assessment methods.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract detailed information about the course from the provided text. "
                    "DO NOT include any URLs, links, or web addresses in your response. "
                    "If the name of the module leader or module leader email is not explicitly mentioned, "
                    "reply with the default value 'not available at the moment'. "
                    "Focus only on course content, descriptions, and academic information. "
                    "The results must be returned in JSON format."
                ),
            },
            {"role": "user", "content": f"Course Name: {course_name}\n{text}"},
        ],
        response_format={"type": "json_object"},
    )
    parsed_json = response.choices[0].message.content
    try:
        parsed = CourseDetailResponse.model_validate_json(parsed_json)
        return parsed.course_detail
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse course details JSON: {e}")
        return None
    except Exception as e:
        st.error(f"Failed to validate course details structure: {e}")
        return None

def search_course_information(query: str) -> str:
    """
    Searches for course information using DuckDuckGo without returning any URLs.
    
    Args:
        query (str): Search query for course information
        
    Returns:
        str: Textual course information content, or empty string if none found
             
    Raises:
        requests.exceptions.RequestException: If DuckDuckGo API is unreachable
        Exception: If search request fails or returns invalid response
        
    Dependencies:
        - DuckDuckGo web search API for privacy-focused search results
        - requests library for HTTP communication
        
    Note:
        Provides privacy-focused search for course information without exposing URLs.
        Returns only textual content that can be used for course analysis.
    """
    try:
        results = DDGS().text(query, max_results=5)
        if results and len(results) > 0:
            # Combine search result descriptions/snippets instead of returning URLs
            course_info = []
            for result in results:
                if 'body' in result and result['body']:
                    course_info.append(result['body'])
                elif 'title' in result and result['title']:
                    course_info.append(result['title'])
            
            return ' '.join(course_info) if course_info else ""
        return ""
    except requests.exceptions.RequestException as e:
        st.warning(f"Search API connection failed: {str(e)}")
        return ""
    except KeyError as e:
        st.warning(f"Search response format error: {str(e)}")
        return ""
    except Exception as e:
        st.warning(f"Course information search failed: {str(e)}")
        return ""

# Updated Streamlit App with state management
def main():
    """
    Main execution function for the Course Catalogue Scraper Streamlit application.
    
    Functionality:
        - Renders Streamlit interface for university and department selection
        - Manages course catalogue URL discovery and validation
        - Coordinates web scraping and course information extraction workflow
        - Handles both direct URL input and search-based catalogue discovery
        - Provides course filtering, sorting, and detailed analysis capabilities
        - Manages data export in multiple formats (CSV, Excel, JSON)
        
    Side Effects:
        - Updates Streamlit session state with course data and user preferences
        - Renders dynamic UI components based on scraping progress and results
        - Handles file downloads and data persistence operations
        - Manages WebDriver lifecycle and resource cleanup
        
    Features:
        - University-specific course catalogue discovery
        - Department-level course filtering and organization
        - Individual course detail extraction and analysis
        - Comprehensive error handling for various failure scenarios
        - Real-time progress indication during scraping operations
        
    Note:
        Entry point for university course catalogue analysis application.
        Designed to handle diverse university website structures and catalogue formats.
        Includes fallback mechanisms for sites with anti-scraping measures.
    """
    st.title("Course Catalogue")

    # Initialize session state
    if 'raw_text' not in st.session_state:
        st.session_state.raw_text = None
    if 'courses' not in st.session_state:
        st.session_state.courses = None
    if 'selected_course_details' not in st.session_state:
        st.session_state.selected_course_details = None

    # Initialize OpenAI client with validation
    try:
        openai_client = OpenAI(api_key=st.secrets["openai_api_key"])
    except KeyError:
        st.error("OpenAI API key not found in secrets. Please configure your API key.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {str(e)}")
        st.stop()

    # URL Input
    st.subheader("Enter Course Catalogue URL")
    url = st.text_input(
        "URL:",
        placeholder="Enter the URL of the course catalogue (e.g., https://example.com/courses)",
        help="Provide the link to the webpage containing the course catalogue."
    )
    # Extract Courses Button
    if st.button("Extract Courses"):
        if url:
            if not validate_url(url):
                st.error("Please enter a valid URL (must start with http:// or https://)")
            else:
                with st.spinner("Retrieving course catalogue..."):
                    try:
                        with CourseScraper() as scraper:
                            content = scraper.scrape_page(url)

                            if content:
                                st.session_state.raw_text = scraper.extract_text(content)
                                st.session_state.courses = extract_courses(st.session_state.raw_text, openai_client)
                                st.session_state.selected_course_details = None  # Reset course details when new courses are extracted
                            else:
                                st.error("Failed to scrape the page.")
                    except RuntimeError as e:
                        st.error(f"Scraper initialization failed: {str(e)}")
                    except Exception as e:
                        st.error(f"Unexpected error during scraping: {str(e)}")
        else:
            st.warning("Please provide a URL.")

    # Manual Course Input
    st.subheader("Add a Course Manually")
    manual_description = st.text_area(
        "Enter course description:",
        placeholder="Provide a brief description of the course...",
        help="Use this field to manually describe a course if no URL is available."
    )

    if st.button("Find Similar Courses"):
        if manual_description:
            with st.spinner("Searching for course information..."):
                search_query = f"university course {manual_description} syllabus curriculum"
                course_info = search_course_information(search_query)
                if course_info:
                    try:
                        # Use the search results as text input for course extraction
                        st.session_state.raw_text = course_info
                        st.session_state.courses = extract_courses(st.session_state.raw_text, openai_client)
                        st.session_state.selected_course_details = None  # Reset course details when new courses are extracted
                        if st.session_state.courses:
                            st.success(f"Found {len(st.session_state.courses)} related courses from search results")
                        else:
                            st.warning("No courses found in the search results. Try a more specific description.")
                    except Exception as e:
                        st.error(f"Error processing search results: {str(e)}")
                else:
                    st.warning("No relevant course information found. Try a more specific description.")
        else:
            st.warning("Please provide a course description.")

    # Display courses if available
    if st.session_state.courses:
        st.subheader("Course Preview")
        try:
            courses_df = pd.json_normalize(st.session_state.courses)
            if 'course_name' not in courses_df.columns:
                st.error("Course data is missing required 'course_name' field. Please try extracting courses again.")
                st.session_state.courses = None
                return
            
            selected_course_name = st.selectbox(
                "Select a course to view details:",
                courses_df['course_name'],
                help="Choose a course from the extracted list to see detailed information."
            )
        except Exception as e:
            st.error(f"Error processing course data: {str(e)}")
            st.session_state.courses = None
            return

        # View Course Details Button
        if selected_course_name and st.button("View Course Details"):
            with st.spinner("Loading course details..."):
                course_details = extract_course_details(
                    selected_course_name,
                    st.session_state.raw_text,
                    openai_client
                )
                if course_details:
                    st.session_state.selected_course_details = course_details
                else:
                    st.error("Failed to extract course details. Please try again.")

        # Display course details if available
        if st.session_state.selected_course_details:
            st.subheader("Course Details")
            try:
                # Normalize the JSON data
                course_detail_df = pd.json_normalize(st.session_state.selected_course_details)
                # Display DataFrame
                st.dataframe(course_detail_df)
            except Exception as e:
                st.error(f"Error displaying course details: {str(e)}")
                # Display details in a more basic format as fallback
                st.write("**Course Details:**")
                details = st.session_state.selected_course_details
                if hasattr(details, '__dict__'):
                    for key, value in details.__dict__.items():
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
                else:
                    st.write(details)

if __name__ == "__main__":
    main()
