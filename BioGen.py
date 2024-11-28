import streamlit as st
import pandas as pd
import re
from langchain.chat_models import ChatOpenAI
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

def search_internet(full_name, university, api_key, model_name):
    query = f"{full_name} {university} academic research"
    
    tool = SerperDevTool(api_key=api_key)
    search_results = tool._run(query)
    
    bio_content = ""
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        bio_content += content + "\n"
    
    if bio_content:
        # Extract structured data from bio_content
        name = full_name
        email = extract_email(bio_content)
        university_location = extract_university_location(bio_content)
        bio = extract_bio(bio_content, name)
        published_papers = extract_published_papers(bio_content)
        
        return [{
            "Name": name,
            "Email": email,
            "University Location": university_location,
            "Bio": bio,
            "Published Papers": published_papers
        }]
    else:
        return "No relevant web results found."

# Helper functions to extract specific information
def extract_email(content):
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
    return email_match.group(0) if email_match else "N/A"

def extract_university_location(content):
    # Try to extract city, then country, and fallback to continent
    city_match = re.search(r'\b(City of \w+|[A-Za-z ]+ City)\b', content)
    if city_match:
        return city_match.group(0)
    country_match = re.search(r'\b(USA|UK|Canada|Germany|France|India|Australia)\b', content, re.IGNORECASE)
    if country_match:
        return country_match.group(0)
    return "Europe"  # Fallback to continent

def extract_published_papers(content):
    # Look for titles of papers and their source
    papers = re.findall(r"“([^”]+)”\s+\(([^)]+)\)", content)
    if papers:
        return ", ".join([f"{title} ({source})" for title, source in papers[:3]])
    return "No published papers found"

def extract_bio(content, name):
    teaching_research_interests = extract_teaching_research_interests(content)
    publications = extract_published_papers(content)
    bio = (
        f"{name} specializes in {teaching_research_interests}. "
        f"Her recent work explores {publications}."
    )
    return bio

def extract_teaching_research_interests(content):
    interests_match = re.search(r"(class|gender|resistance|liberation|social justice|sovereignty|economic).*", content, re.IGNORECASE)
    return interests_match.group(0) if interests_match else "varied academic interests"

def display_results_in_table(results):
    if isinstance(results, list):
        df = pd.DataFrame(results)
        st.table(df)  # Display as a table in Streamlit
    else:
        st.write(results)

# Main function
def main():
    st.title("Desktop Research")
    st.markdown("Search for academic profiles by querying local files (CSV/XLSX) or the internet.")

    # User inputs for API configuration
    st.markdown("### API Configuration")
    api_key = st.text_input("API Key", type="password", help="Enter your API key for accessing OpenAI or other models.")
    model_name = st.selectbox("Choose a Model", ["OpenAI GPT-4", "OpenAI GPT-3.5", "Custom Model"], help="Select the model to use for extracting information.")
    
    # User inputs for searching profiles
    full_name = st.text_input("Full Name (First and Last Name)")
    university = st.text_input("University")

    # Option to search local files or the internet
    search_scope = st.selectbox("Where would you like to search?", ["Local Files", "Internet", "Both"])
    
    # File Upload Section (Optional for local file search)
    uploaded_files = st.file_uploader("Upload CSV/XLSX files (optional for local search)", type=["csv", "xlsx"], accept_multiple_files=True)
    
    if st.button("Search"):
        if search_scope in ["Local Files", "Both"] and not uploaded_files and search_scope == "Local Files":
            st.warning("You selected local file search but didn't upload any files. Switching to Internet search...")
            search_scope = "Internet"
            
        if search_scope in ["Local Files", "Both"]:
            if uploaded_files:
                for file in uploaded_files:
                    if file.name.endswith(".csv"):
                        df = pd.read_csv(file)
                    elif file.name.endswith(".xlsx"):
                        df = pd.read_excel(file)
                    
                    local_results = search_local_file(df, full_name, university)
                    st.write("Results from Local Files:")
                    display_results_in_table(local_results)
        
        if search_scope in ["Internet", "Both"]:
            web_results = search_internet(full_name, university, api_key, model_name)
            st.write("Results from Internet:")
            display_results_in_table(web_results)

# Run the app
if __name__ == "__main__":
    main()
