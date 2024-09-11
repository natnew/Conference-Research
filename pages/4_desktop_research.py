import streamlit as st
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from con_research.src.modules.scrapping_module import ContentScraper, scrape_faculty_page
from con_research.src.modules.search_module import SerperDevTool

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

def search_internet(full_name, university, serper_api_key):
    # Generate a search query
    query = f"{full_name} {university} academic research"
    
    # Use Serper or another web scraping/search tool
    tool = SerperDevTool(api_key=serper_api_key)
    search_results = tool._run(query)
    
    # Scrape relevant content from search results
    bio_content = ""
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        bio_content += content + "\n"
    
    return bio_content if bio_content else "No relevant web results found."

def display_results_in_table(results):
    if isinstance(results, list):
        # Convert list of dicts into a DataFrame
        df = pd.DataFrame(results)
        df.columns = ['Name', 'Email', 'University', 'University Location', 'Bio', 'Social Handle', 'Published Papers']
        st.table(df)  # Display as a table in Streamlit
    else:
        st.write(results)  # Display the error message

# Function to scrape professors based on interests from a URL
def scrape_professors_from_url(url, interests):
    # Check if the URL and interests are valid
    if not url or not interests:
        return "Please provide both URL and interest areas."
    
    keywords = [kw.strip().lower() for kw in interests.split(',')]  # Convert interests into keywords list
    result = scrape_faculty_page(url, keywords)  # Call the scraping function
    
    if isinstance(result, list) and result:
        return result  # Return matching profiles
    return "No matching profiles found."

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

    # Option to search local files, internet, or fetch from a URL
    search_scope = st.selectbox("Where would you like to search?", ["Local Files", "Internet", "Web URL", "Both"])
    
    # File Upload Section (Optional for local file search)
    uploaded_files = st.file_uploader("Upload CSV/XLSX files (optional for local search)", type=["csv", "xlsx"], accept_multiple_files=True)
    
    # URL and interests input for fetching profiles from a web page
    if search_scope == "Web URL":
        url = st.text_input("Enter the webpage URL for scraping faculty profiles")
        interests = st.text_area("Enter keywords for interests (comma separated)", "child development, diversity")
    
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
        
        if search_scope == "Web URL":
            # Search by scraping the URL
            if url and interests:
                url_results = scrape_professors_from_url(url, interests)
                st.write("Results from URL:")
                display_results_in_table(url_results)
            else:
                st.warning("Please provide both a URL and interest areas.")

# Run the app
if __name__ == "__main__":
    main()
