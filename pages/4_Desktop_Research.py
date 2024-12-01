import streamlit as st
import pandas as pd
#from con_research.src.modules.scrapping_module import ContentScraper
#from con_research.src.modules.search_module import SerperDevTool

st.sidebar.title(":streamlit: Conference Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content 
and assists in lead generation. Designed to support academic and professional 
activities, it offers interconnected modules that streamline research tasks, 
whether for conferences, campus visits, or other events.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This app leverages cutting-edge technologies to automate and enhance research 
    workflows. It combines generative AI, voice-to-action capabilities, 
    Retrieval-Augmented Generation (RAG), agentic RAG, and other advanced 
    methodologies to deliver efficient and accurate results.

    """)
    
with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
       "Search for academic profiles by querying local files (CSV/XLSX) or the internet. Combine the power of local data and web scraping to uncover detailed academic profiles."
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    openai_api_key = st.secrets["openai_api_key"]

# Define your helper functions
def search_local_file(df, full_name, university):
    # Split the full name into first and last name
    name_parts = full_name.split()
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""  # Handle cases where there's no last name
    
    # Function to search Excel/CSV files
    result = df[(df['First Name'] == first_name) & (df['Last Name'] == last_name) & (df['University'] == university)]
    if not result.empty:
        return result.to_dict(orient='records')
    return "No information found in local files."

def search_internet(full_name, university, research_interest, serper_api_key):
    query = f"{full_name} {university} {research_interest} academic research"
    
    # Use Serper or another web scraping/search tool
    tool = SerperDevTool(api_key=serper_api_key)  # No temperature here
    search_results = tool._run(query)

    bio_content = ""
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        bio_content += content + "\n"
    
    return bio_content if bio_content else "No relevant web results found."


# Function to display the results with clear formatting
def display_results(professor_data):
    for prof in professor_data:
        st.write(f"### Name: {prof.get('Name', 'N/A')}")
        st.write(f"**University**: {prof.get('University', 'N/A')}")
        st.write(f"**Teaching Interest**: {prof.get('Teaching Interest', 'N/A')}")
        st.write(f"**Research Interest**: {prof.get('Research Interest', 'N/A')}")
        st.write(f"**Contact**: {prof.get('Contact', 'N/A')}")
        st.write(f"**Bio**: {prof.get('Bio', 'N/A')}")
        st.write("---")

# Main function
def main():
    st.title("Desktop Research")
    st.markdown("Search for academic profiles by querying local files (CSV/XLSX) or the internet. :balloon:")
    
    # API Key Inputs
    groq_api_key = st.text_input("Groq API Key", type="password")
    serper_api_key = st.secrets["serper_api_key"]  # Assuming Serper API is used for web scraping

    # User input for full name (first and last name combined)
    full_name = st.text_input("Full Name (First and Last Name)")

    # Input for research or teaching interests
    research_interest = st.text_input("Research or Teaching Interest")

    # Input for university
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
                    if isinstance(local_results, list):
                        display_results(local_results)
                    else:
                        st.write(local_results)
            else:
                st.warning("Please upload a file to search in local data.")

        if search_scope in ["Internet", "Both"]:
            # Search on the internet using Serper
            web_results = search_internet(full_name, university, research_interest, serper_api_key)
            st.write("Results from Internet:")
            st.write(web_results)

# Run the app
if __name__ == "__main__":
    main()
