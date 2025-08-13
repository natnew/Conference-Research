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
- Dependencies: streamlit, selenium, webdriver-manager, beautifulsoup4, pandas, pydantic, openai, requests, ddgs
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
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from openai import OpenAI
import openai
import requests
from duckduckgo_search import DDGS



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
        ...,
        description="The email of the module leader explicitly mentioned in the text. If not available, respond with 'not available at the moment'."
    )
class CourseCatalogueResponse(BaseModel):
    courses: List[CoursePreview]

class CourseDetailResponse(BaseModel):
    course_detail:CourseDetail

# Selenium WebDriver setup remains the same
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

# Enhanced CourseScraper class with context manager
class CourseScraper:
    def __init__(self):
        self.driver = get_chrome_driver()
        if not self.driver:
            st.error("Failed to initialize the scraper")
            st.stop()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                st.error(f"Error closing WebDriver: {str(e)}")

    def __del__(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def scrape_page(self, url: str, wait_time: int = 7) -> str:
        try:
            self.driver.get(url)
            time.sleep(wait_time)
            return self.driver.page_source
        except Exception as e:
            st.error(f"Error accessing URL: {str(e)}")
            return ""

    def extract_text(self, content: str) -> str:
        """Enhanced text extraction with course content filtering."""
        soup = BeautifulSoup(content, 'html.parser')
        
        # Remove navigation, footer, and administrative content
        for element in soup(['nav', 'footer', 'header', 'aside', 'script', 'style']):
            element.decompose()
        
        # Remove common non-course elements by class names
        for element in soup.find_all(attrs={'class': re.compile(r'navigation|menu|footer|sidebar|banner', re.I)}):
            element.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        return re.sub(r'\n\s*\n', '\n\n', text)

def validate_course_names(courses: List[CoursePreview]) -> List[CoursePreview]:
    """
    Filter out invalid or generic course names using pattern matching.
    
    Args:
        courses: List of extracted course previews
        
    Returns:
        Filtered list of valid course names
    """
    # Common phrases to exclude
    excluded_patterns = [
        r'english language.*usage',
        r'language requirement',
        r'language proficiency',
        r'general information',
        r'contact us',
        r'about us',
        r'navigation',
        r'home page',
        r'search',
        r'login',
        r'register',
        r'privacy policy',
        r'terms of service',
        r'admissions',
        r'student services',
        r'apply now',
        r'download',
        r'view all',
        r'more info',
        r'click here'
    ]
    
    validated_courses = []
    for course in courses:
        course_name_lower = course.course_name.lower().strip()
        
        # Skip if matches excluded patterns
        if any(re.search(pattern, course_name_lower) for pattern in excluded_patterns):
            continue
            
        # Skip if too short or too generic
        if len(course.course_name.strip()) < 5:
            continue
            
        # Skip if all caps (likely navigation/header text)
        if course.course_name.isupper() and len(course.course_name) < 50:
            continue
            
        # Skip if contains common non-course indicators
        if any(indicator in course_name_lower for indicator in ['©', 'copyright', 'all rights', 'cookie', 'policy']):
            continue
            
        validated_courses.append(course)
    
    return validated_courses

def validate_url(url: str) -> bool:
    """
    Validate URL format and accessibility.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid and accessible
    """
    # Basic URL format validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        st.error("Please enter a valid URL format (e.g., https://example.com)")
        return False
    
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code >= 400:
            st.error(f"URL returned status code: {response.status_code}")
            return False
        return True
    except requests.RequestException as e:
        st.error(f"Unable to access URL: {str(e)}")
        return False

# Enhanced course extraction with improved AI prompt specificity
def extract_courses(text: str, openai_client: OpenAI) -> List[CoursePreview]:
    """
    Extract course names from academic text with improved specificity and error handling.
    
    Args:
        text: Raw text content from course catalogue page
        openai_client: Initialized OpenAI client
        
    Returns:
        List of CoursePreview objects with extracted course names
        
    Raises:
        Exception: Logs errors but returns empty list to maintain application flow
    """
    try:
        response = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system", 
                    "content": """Extract ONLY actual academic course titles from the provided text. 
                    
                    INCLUDE:
                    - Specific subject courses (e.g., "Introduction to Psychology", "Advanced Mathematics", "Molecular Biology")
                    - Degree program modules (e.g., "Research Methods", "Final Year Project", "Dissertation")
                    - Specialized academic topics with clear educational content
                    - Named course codes with descriptions (e.g., "PSYC101: Introduction to Psychology")
                    - Academic seminars and workshops that are part of formal curriculum
                    
                    EXCLUDE:
                    - General university requirements (e.g., "English language & usage", "Language proficiency")
                    - Navigation menu items (e.g., "Home", "About", "Contact")
                    - Administrative information (e.g., "Admissions", "Student Services")
                    - Generic text about language proficiency or entry requirements
                    - Footer content, copyright notices, or contact information
                    - University policies, general descriptions, or mission statements
                    - Search functionality, login prompts, or website navigation
                    - Degree names without specific course content (e.g., "Bachelor of Arts")
                    
                    Focus on courses that students would actually enroll in as part of their academic program.
                    Return only legitimate academic course names with substantive educational content."""
                },
                {"role": "user", "content": text}
            ],
            response_format=CourseCatalogueResponse,
            timeout=30
        )
        courses_data = response.choices[0].message.content
        courses_parsed = json.loads(courses_data)
        courses_list = courses_parsed.get("courses", [])
        
        # Apply post-processing validation
        validated_courses = validate_course_names(courses_list)
        return validated_courses
        
    except openai.OpenAIError as e:
        st.error(f"OpenAI API error: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Unexpected error during course extraction: {str(e)}")
        return []

# Extract course details function with improved error handling
def extract_course_details(course_name: str, text: str, openai_client: OpenAI) -> CourseDetail:
    """
    Extract detailed course information with enhanced error handling.
    
    Args:
        course_name: Name of the course to extract details for
        text: Raw text content containing course information
        openai_client: Initialized OpenAI client
        
    Returns:
        CourseDetail object with extracted information
        
    Raises:
        Exception: Logs errors but returns None to maintain application flow
    """
    try:
        response = openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {
                    "role": "system", 
                    "content": """Extract detailed information about the specific course from the provided text. 
                    
                    REQUIRED INFORMATION:
                    - Course name (exact match from text)
                    - Course overview (brief summary of content and objectives)
                    - Course details (comprehensive description including structure, modules, assessment)
                    - Module leader name (look for titles: Director, Senior Lecturer, Associate Professor, Professor)
                    - Module leader email (if explicitly mentioned)
                    
                    IMPORTANT: If module leader name or email is not explicitly mentioned in the text, 
                    respond with 'not available at the moment' for those fields.
                    
                    Focus only on the specified course and ignore general university information."""
                },
                {"role": "user", "content": f"Course Name: {course_name}\n{text}"}
            ],
            response_format=CourseDetailResponse,
            timeout=30
        )
        course_detail_data = response.choices[0].message.content
        course_detail_data_parsed = json.loads(course_detail_data)
        course_details = course_detail_data_parsed.get("course_detail", {})
        return course_details
        
    except openai.OpenAIError as e:
        st.error(f"OpenAI API error while extracting course details: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse course details response: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error during course detail extraction: {str(e)}")
        return None

# Function to search DuckDuckGo
def search_duckduckgo(query: str) -> str:
    results = DDGS().text(query, max_results=5)
    if results:
        return results[0]['href']  # Return the first URL found
    return ""

# Updated Streamlit App with state management
def main():
    st.title("Course Catalogue")

    # Initialize session state
    if 'raw_text' not in st.session_state:
        st.session_state.raw_text = None
    if 'courses' not in st.session_state:
        st.session_state.courses = None
    if 'selected_course_details' not in st.session_state:
        st.session_state.selected_course_details = None

    openai_key = st.secrets.get("openai_api_key")
    if not openai_key:
        st.error("OpenAI API key is not configured. Please add 'openai_api_key' to Streamlit secrets.")
        return
    openai_client = OpenAI(api_key=openai_key)

    # URL Input
    st.subheader("Enter Course Catalogue URL")
    url = st.text_input(
        "URL:",
        placeholder="Enter the URL of the course catalogue (e.g., https://example.com/courses)",
        help="Provide the link to the webpage containing the course catalogue."
    )
    # Extract Courses Button
    if st.button("Extract Courses"):
        if url and validate_url(url):
            with st.spinner("Retrieving course catalogue..."):
                with CourseScraper() as scraper:
                    content = scraper.scrape_page(url)

                    if content:
                        st.session_state.raw_text = scraper.extract_text(content)
                        st.session_state.courses = extract_courses(st.session_state.raw_text, openai_client)
                        st.session_state.selected_course_details = None  # Reset course details when new courses are extracted
                    else:
                        st.error("Failed to scrape the page.")
        elif url:
            # URL validation failed, error message already shown by validate_url
            pass
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
            with st.spinner("Retrieving course catalogue..."):
                search_query = f" a similar detailed course catalogue for {manual_description}"
                url = search_duckduckgo(search_query)
                if url:
                    with CourseScraper() as scraper:
                        content = scraper.scrape_page(url)

                        if content:
                            st.session_state.raw_text = scraper.extract_text(content)
                            st.session_state.courses = extract_courses(st.session_state.raw_text, openai_client)
                            st.session_state.selected_course_details = None  # Reset course details when new courses are extracted
                        else:
                            st.error("Failed to scrape the page.")
                else:
                    st.warning("No relevant URL found.")
        else:
            st.warning("Please provide a course description.")

    # Display courses if available
    if st.session_state.courses:
        st.subheader("Course Preview")
        courses_df = pd.json_normalize(st.session_state.courses)
        selected_course_name = st.selectbox(
            "Select a course to view details:",
            courses_df['course_name'],
            help="Choose a course from the extracted list to see detailed information."
        )

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
            # Normalize the JSON data
            course_detail_df = pd.json_normalize(st.session_state.selected_course_details)
            # Display DataFrame
            st.dataframe(course_detail_df)

if __name__ == "__main__":
    main()
