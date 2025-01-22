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
        description="The name of the module leader explicitly mentioned in the text. If not available, respond with 'not available at the moment'."
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

# Scraper class remains the same
class CourseScraper:
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

# Extract courses function remains the same
def extract_courses(text: str, openai_client: OpenAI) -> List[CoursePreview]:
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "Extract a detailed list, of course, names as described  from the provided text. Return results as a structured output defined in the response mode of the model."},
            {"role": "user", "content": text}
        ],
        response_format=CourseCatalogueResponse
    )
    courses_data = response.choices[0].message.content
    courses_parsed = json.loads(courses_data)
    courses_list = courses_parsed.get("courses", [])
    return courses_list

# Extract course details function remains the same
def extract_course_details(course_name: str, text: str, openai_client: OpenAI) -> CourseDetail:
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "Extract detailed information about the course from the provided text if the name of the module leader or module leader email is not  explicitly mentioned  just leave it as an empty string '' or None."},
            {"role": "user", "content": f"Course Name: {course_name}\n{text}"}
        ],
        response_format=CourseDetailResponse
    )
    course_detail_data = response.choices[0].message.content
    course_detail_data_parsed = json.loads(course_detail_data)
    course_details = course_detail_data_parsed.get("course_detail", [])
    return course_details

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

    openai_client = OpenAI(api_key=st.secrets["openai_api_key"])

    # URL Input
    st.subheader("Enter Course Catalogue URL")
    url = st.text_input(
        "URL:",
        placeholder="Enter the URL of the course catalogue (e.g., https://example.com/courses)",
        help="Provide the link to the webpage containing the course catalogue."
    )
    wait_time = st.slider(
        "Page Load Wait Time (seconds)",
        min_value=1, max_value=15, value=5,
        help="Set the wait time to allow the page to fully load before scraping."
    )

    # Extract Courses Button
    if st.button("Extract Courses"):
        if url:
            scraper = CourseScraper()
            content = scraper.scrape_page(url, wait_time)

            if content:
                st.session_state.raw_text = scraper.extract_text(content)
                st.session_state.courses = extract_courses(st.session_state.raw_text, openai_client)
                st.session_state.selected_course_details = None  # Reset course details when new courses are extracted
            else:
                st.error("Failed to scrape the page.")
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
            search_query = f" a similar detailed course catalogue for {manual_description}"
            url = search_duckduckgo(search_query)
            if url:
                scraper = CourseScraper()
                content = scraper.scrape_page(url, wait_time)

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
            st.session_state.selected_course_details = extract_course_details(
                selected_course_name,
                st.session_state.raw_text,
                openai_client
            )

        # Display course details if available
        if st.session_state.selected_course_details:
            st.subheader("Course Details")
            # Normalize the JSON data
            course_detail_df = pd.json_normalize(st.session_state.selected_course_details)
            # Display DataFrame
            st.dataframe(course_detail_df)

if __name__ == "__main__":
    main()
