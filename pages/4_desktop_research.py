import streamlit as st
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import yaml
from con_research.src.modules.scrapping_module import ContentScraper
from con_research.src.modules.search_module import SerperDevTool

# Define your helper functions
def search_local_file(df, first_name, last_name, university):
    # Function to search Excel/CSV files
    result = df[(df['First Name'] == first_name) & (df['Last Name'] == last_name) & (df['University'] == university)]
    if not result.empty:
        return result.to_dict(orient='records')
    return "No information found in local files."

def search_internet(first_name, last_name, university, serper_api_key):
    # Generate a search query
    query = f"{first_name} {last_name} {university} academic research"

    # Use Serper or another web scraping/search tool
    tool = SerperDevTool(api_key=serper_api_key)
    search_results = tool._run(query)

    # Scrape relevant content from search results
    bio_content = ""
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        bio_content += content + "\n"

    return bio_content if bio_content else "No relevant web results found."

# Main function
def main():
    st.title("Desktop Research")
    st.markdown("Search for academic profiles by querying local files (CSV/XLSX) or the internet.")

    # API Key Inputs
    groq_api_key = st.text_input("Groq API Key", type="password")
    serper_api_key = st.secrets["serper_api_key"]  # Assuming Serper API is used for web scraping

    # User inputs for searching profiles
    first_name = st.text_input("First Name")
    last_name = st.text_input("Last Name")
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
                    local_results = search_local_file(df, first_name, last_name, university)
                    st.write("Results from Local Files:")
                    st.write(local_results)
            else:
                st.warning("Please upload a file to search in local data.")

        if search_scope in ["Internet", "Both"]:
            # Search on the internet using Serper
            web_results = search_internet(first_name, last_name, university, serper_api_key)
            st.write("Results from Internet:")
            st.write(web_results)

# Run the app
if __name__ == "__main__":
    main()
