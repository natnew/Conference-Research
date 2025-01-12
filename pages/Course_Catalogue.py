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

# Pydantic models for structured output
class CoursePreview(BaseModel):
    course_name: str

class CourseDetail(BaseModel):
    course_name: str
    course_overview: str
    course_details: str
    module_leaders: List[Dict[str, str]] = Field(description="This is an example of the module leaders: {'name': 'John Doe', 'email': 'john.doe@example.com'}")
    reading_list: List[str]

class CourseCatalogueResponse(BaseModel):
    courses: List[CoursePreview]

class CourseDetailResponse(BaseModel):
    course_detail: CourseDetail

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

# Extract courses using LLM
def extract_courses(text: str, openai_client: OpenAI) -> List[CoursePreview]:
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "Extract a list of courses with their names and overviews from the following text. Return results as a structured output defined in the response mode of the model."},
            {"role": "user", "content": text}
        ],
        response_format=CourseCatalogueResponse
    )
    courses_data = response.choices[0].message.content
    courses_parsed = json.loads(courses_data)
    courses_list = courses_parsed.get("courses", [])
    return courses_list

# Extract course details using LLM
def extract_course_details(course_name: str, text: str, openai_client: OpenAI) -> CourseDetail:
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "Extract detailed information about the course from the following text."},
            {"role": "user", "content": f"Course Name: {course_name}\n{text}"}
        ],
        response_format=CourseDetailResponse
    )
    course_detail_data = response.choices[0].message.content
    st.write("Debug: course_detail_data", course_detail_data)
    course_detail_data_dict = json.loads(course_detail_data)  # Convert the JSON string to a dictionary
    course_detail_response = CourseDetailResponse(**course_detail_data_dict)
    return course_detail_response.course_detail

# Streamlit App
def main():
    st.title("Course Catalogue")

    openai_client = OpenAI(api_key=st.secrets["openai_api_key"])

    # URL Input
    url = st.text_input("Enter Course Catalogue URL:")
    wait_time = st.slider("Page Load Wait Time (seconds)", min_value=1, max_value=15, value=5)
    
    if st.button("Extract Courses"):
        if url:
            scraper = CourseScraper()
            content = scraper.scrape_page(url, wait_time)

            if content:
                raw_text = scraper.extract_text(content)
                courses = extract_courses(raw_text, openai_client)
                courses_df = pd.json_normalize(courses)
                st.subheader("Course Preview")
                selected_course_name = st.selectbox(
                    "Select a course to view details:", courses_df['course_name']
                )

                if selected_course_name:
                    if st.button("View Course Details"):
                        course_details = extract_course_details(selected_course_name, raw_text, openai_client)

                        st.subheader("Course Details")
                        st.write(f"**Course Name:** {course_details.course_name}")
                        st.write(f"**Overview:** {course_details.course_overview}")
                        st.write(f"**Details:** {course_details.course_details}")

                        st.write("**Module Leaders/Coordinators:**")
                        for leader in course_details.module_leaders:
                            st.write(f"- {leader['name']} ({leader['email']})")

                        st.write("**Reading List:**")
                        st.write("\n".join(course_details.reading_list))
            else:
                st.error("Failed to scrape the page.")
        else:
            st.warning("Please provide a URL.")

    # # Manual Course Input
    # st.subheader("Add a Course Manually")
    # manual_description = st.text_area("Enter course description:")

    # if st.button("Find Similar Courses"):
    #     if manual_description:
    #         similar_courses = extract_courses(manual_description, openai_client)
    #         st.write(similar_courses)
    #     else:
    #         st.warning("Please provide a course description.")

if __name__ == "__main__":
    main()
