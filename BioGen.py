import streamlit as st
import pandas as pd
import re
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import yaml
from con_research.src.modules.scrapping_module import ContentScraper
from con_research.src.modules.search_module import SerperDevTool

# Define your helper functions
def search_local_file(df, full_name, university):
    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""
    result = df[(df['First Name'] == first_name) & (df['Last Name'] == last_name) & (df['University'] == university)]
    if not result.empty:
        return result.to_dict(orient='records')
    return "No information found in local files."

def search_internet(full_name, university, serper_api_key):
    query = f"{full_name} {university} academic research"
    
    tool = SerperDevTool(api_key=serper_api_key)
    search_results = tool._run(query)
    
    bio_content = ""
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        bio_content += content + "\n"
    
    if bio_content:
        # Extract structured data from bio_content
        name = full_name
        email = extract_email(bio_content)
        university_name = university
        university_location = extract_university_location(bio_content)
        bio = extract_bio(bio_content)
        social_handle = extract_social_handle(bio_content)
        published_papers = extract_published_papers(bio_content)
        
        return [{
            "Name": name,
            "Email": email,
            "University": university_name,
            "University Location": university_location,
            "Bio": bio,
            "Social Handle": social_handle,
            "Published Papers": published_papers
        }]
    else:
        return "No relevant web results found."

# Helper functions to extract specific information
def extract_email(content):
    # Regular expression to find email
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    return email_match.group(0) if email_match else "N/A"

def extract_university_location(content):
    # Dummy function to extract university location
    location_match = re.search(r'(University of \w+)', content)
    return location_match.group(0) if location_match else "N/A"

def extract_bio(content):
    # Return part of the content that seems like a bio
    return content[:500]  # Limiting to 500 characters for simplicity

def extract_social_handle(content):
    # Dummy function to extract social handle
    handle_match = re.search(r'@[A-Za-z0-9_]+', content)
    return handle_match.group(0) if handle_match else "N/A"

def extract_published_papers(content):
    # Dummy function to simulate extracting published papers
    return "Paper 1, Paper 2, Paper 3"

def display_results_in_table(results):
    if isinstance(results, list):
        # Convert list of dicts into a DataFrame
        df = pd.DataFrame(results)
        df.columns = ['Name', 'Email', 'University', 'University Location', 'Bio', 'Social Handle', 'Published Papers']
        st.table(df)  # Display as a table in Streamlit
    else:
        st.write(results)  # Display the error message

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

    # Option to search local files or the internet
    search_scope = st.selectbox("Where would you like to search?", ["Local Files", "Internet", "Both"])
    
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
            # Search on the internet using Serper
            web_results = search_internet(full_name, university, serper_api_key)
            st.write("Results from Internet:")
            display_results_in_table(web_results)

# Run the app
if __name__ == "__main__":
    main()
