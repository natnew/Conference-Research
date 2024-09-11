import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from con_research.src.modules.scrapping_module import ContentScraper, scrape_faculty_page
from con_research.src.modules.search_module import SerperDevTool
from con_research.src.modules.scrape_professors import scrape_professors_by_research_area

import os

def load_interest_areas():
    # Build the correct path to the interests.json file
    json_file_path = os.path.join(os.path.dirname(__file__), '..', 'con_research', 'data', 'interests.json')
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data['interest_areas']


# Define your helper functions
def search_local_file(df, full_name, university):
    # Function to search Excel/CSV files
    name_parts = full_name.split()  # Split full name into parts
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""  # Assume last name is the second part
    result = df[(df['First Name'] == first_name) & (df['Last Name'] == last_name) & (df['University'] == university)]
    if not result.empty:
        return result.to_dict(orient='records')
    return "No information found in local files."

def search_internet(full_name, university, selected_interest, serper_api_key):
    # Generate a search query with full name, university, and selected interest
    query = f"{full_name} {university} professor {selected_interest} academic research"
    
    # Use Serper or another web scraping/search tool
    tool = SerperDevTool(api_key=serper_api_key)
    search_results = tool._run(query)
    
    # Scrape relevant content from search results
    professors = []
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        # Extract professor-specific information
        prof_data = extract_professor_data(content)
        if prof_data:
            professors.append(prof_data)
    
    return professors if professors else "No relevant web results found."

def extract_professor_data(content):
    """
    Function to extract concise professor information like name, bio, and email from the page content.
    """
    soup = BeautifulSoup(content, 'html.parser')
    professor_data = {
        'name': None,
        'bio': None,
        'email': None
    }

    # Example tags for extracting relevant details (adjust according to actual HTML structure)
    name_tag = soup.find('h1')  # Adjust based on actual page structure
    bio_tag = soup.find('p')     # Adjust based on actual page structure
    email_tag = soup.find('a', href=lambda href: href and "mailto:" in href)

    if name_tag:
        professor_data['name'] = name_tag.get_text(strip=True)
    if bio_tag:
        professor_data['bio'] = bio_tag.get_text(strip=True)[:150] + "..."  # Limit bio length for brevity
    if email_tag:
        professor_data['email'] = email_tag.get('href').replace("mailto:", "")
    
    # Only return if name and bio are found
    return professor_data if professor_data['name'] and professor_data['bio'] else None

def display_results_in_table(professors):
    if isinstance(professors, list) and professors:
        for prof in professors:
            st.write(f"**Name**: {prof['name']}")
            st.write(f"**Bio**: {prof['bio']}")
            st.write(f"**Email**: {prof['email'] if prof['email'] else 'No email available'}")
            st.write("---")
    else:
        st.write(professors)


# Main function
def main():
    st.title("Desktop Research")
    st.markdown("Search for academic profiles by querying local files (CSV/XLSX) or the internet.")

    # API Key Inputs
    groq_api_key = st.text_input("Groq API Key", type="password")
    serper_api_key = st.secrets["serper_api_key"]  # Assuming Serper API is used for web scraping
    
    # User inputs for searching profiles (combine first name and last name)
    full_name = st.text_input("Full Name (First and Last Name)")
    university = st.text_input("University")

    # Option to search local files or internet
    search_scope = st.selectbox("Where would you like to search?", ["Local Files", "Internet", "Both"])

    # Interest area selection from dropdown (loaded from JSON)
    interest_areas = load_interest_areas()
    selected_interest = st.selectbox("Select Interest Area", interest_areas)

    # File Upload Section (Optional for local file search)
    uploaded_files = st.file_uploader("Upload CSV/XLSX files (optional for local search)", type=["csv", "xlsx"], accept_multiple_files=True)

    if st.button("Search"):
        if search_scope in ["Local Files", "Both"]:
            # Process local file search
            if uploaded_files:
                for file in uploaded_files:
                    # Load CSV or Excel file
                    if file.name.endswith(".csv"):
                        df = pd.read_csv(file)
                    elif file.name.endswith(".xlsx"):
                        df = pd.read_excel(file)
    
                    # Search in the file
                    local_results = search_local_file(df, full_name, university)
                    st.write("Results from Local Files:")
                    display_results_in_table(local_results)
            else:
                st.warning("Please upload a file to search in local data.")
    
        if search_scope in ["Internet", "Both"]:
            # Ensure that full_name, university, and selected_interest are passed
            web_results = search_internet(full_name, university, selected_interest, serper_api_key)
            st.write(f"Results for {selected_interest} in {university}:")
            display_results_in_table(web_results)


# Run the app
if __name__ == "__main__":
    main()
