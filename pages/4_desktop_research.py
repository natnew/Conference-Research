import streamlit as st
import pandas as pd
import json
from con_research.src.modules.search_module import SerperDevTool
from con_research.src.modules.scrapping_module import ContentScraper

# Load interest areas from the JSON file stored in the data folder
def load_interest_areas():
    with open('con_research/data/interests.json', 'r') as f:
        data = json.load(f)
    return data['interest_areas']

# Function to scrape and extract professor data (name, bio, email)
def extract_professor_data(url):
    page_content = ContentScraper.scrape_anything(url)
    
    # Basic extraction logic, assuming the page contains professor details in <h1> (name), <p> (bio), <a> (email)
    # This would need to be adjusted based on the actual structure of the professor's profile page
    professor_data = {
        'name': None,
        'bio': None,
        'email': None
    }

    # Example for finding name and bio (adjust as needed based on actual structure)
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # Extract professor's name
    name_tag = soup.find('h1')
    if name_tag:
        professor_data['name'] = name_tag.get_text(strip=True)
    
    # Extract professor's bio (usually in a <p> tag, adjust as needed)
    bio_tag = soup.find('p')
    if bio_tag:
        professor_data['bio'] = bio_tag.get_text(strip=True)
    
    # Extract email (if available, adjust if it's in a different tag)
    email_tag = soup.find('a', href=lambda href: href and "mailto:" in href)
    if email_tag:
        professor_data['email'] = email_tag.get('href').replace("mailto:", "")
    
    return professor_data

# Search the internet for professors with a specific interest from a university
def search_internet_for_professors(university, interest, serper_api_key):
    # Generate a search query to find professors from the university with the interest area
    query = f"{university} professor {interest} academic research"
    
    # Use SerperDevTool or another web scraping/search tool
    tool = SerperDevTool(api_key=serper_api_key)
    search_results = tool._run(query)
    
    professors = []
    for url in search_results:
        professor_data = extract_professor_data(url)
        if professor_data['name'] and professor_data['bio']:
            professors.append(professor_data)
    
    return professors if professors else "No relevant professors found."

# Display search results in a user-friendly format
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
    st.markdown("Search for academic profiles by university and interest area.")

    # API Key Input (for web searching)
    serper_api_key = st.secrets["serper_api_key"]
    
    # User inputs for searching profiles
    university = st.text_input("University Name")

    # Load interest areas from the JSON file in the data folder
    interest_areas = load_interest_areas()
    selected_interest = st.selectbox("Select Interest Area", interest_areas)

    if st.button("Search"):
        if university and selected_interest:
            professors = search_internet_for_professors(university, selected_interest, serper_api_key)
            st.write(f"Results for {selected_interest} at {university}:")
            display_results_in_table(professors)
        else:
            st.warning("Please provide both a university name and select an interest area.")

# Run the app
if __name__ == "__main__":
    main()
