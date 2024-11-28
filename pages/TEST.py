import streamlit as st
import pandas as pd
from con_research.src.modules.scrapping_module import ContentScraper
from con_research.src.modules.search_module import SerperDevTool

# App Sidebar Configuration
st.sidebar.title("Conference Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content 
and assists in lead generation. Designed to support academic and professional 
activities, it offers interconnected modules that streamline research tasks, 
whether for conferences, campus visits, or other events.
""")

with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This app leverages cutting-edge technologies to automate and enhance research 
    workflows. It combines generative AI, voice-to-action capabilities, 
    Retrieval-Augmented Generation (RAG), agentic RAG, and other advanced 
    methodologies to deliver efficient and accurate results.
    """)

# Internet Search Function
def search_internet(full_name, university, research_interest):
    """
    Search for academic profiles on the internet using the Serper API.
    """
    # Access the API key from Streamlit secrets
    serper_api_key = st.secrets["serper_api_key"]
    
    query = f"{full_name} {university} {research_interest} academic research"
    
    # Use SerperDevTool for web scraping and searching
    tool = SerperDevTool(api_key=serper_api_key)
    search_results = tool._run(query)

    bio_content = ""
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        bio_content += content + "\n"
    
    return bio_content if bio_content else "No relevant web results found."

st.title("BioGen - Chunk-Based Bio Generator")

# Helper Function for Bio Generation
def generate_bio(row):
    """
    Generate a bio for a given row of data.
    """
    name = row.get('Name', 'N/A')
    profession = row.get('Profession', 'N/A')
    specialization = row.get('Specialization', 'N/A')
    university = row.get('University', 'N/A')
    research_interest = row.get('Research Interest', 'N/A')
    teaching_interest = row.get('Teaching Interest', 'N/A')
    contact_details = row.get('Contact Details', 'N/A')
    
    return (f"{name} is a {profession} specializing in {specialization}, currently affiliated with {university}. "
            f"Their research interests include {research_interest}, and they are passionate about teaching {teaching_interest}. "
            f"You can reach out to them at {contact_details}.")

# File Upload
uploaded_file = st.file_uploader("Upload your CSV/XLSX file", type=["csv", "xlsx"])
if uploaded_file:
    # Load File
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.write("### File Preview:")
    st.write(data.head())

    # Specify Chunk Size
    chunk_size = st.number_input("Number of rows per chunk", min_value=1, max_value=len(data), value=10)
    total_chunks = (len(data) + chunk_size - 1) // chunk_size
    st.write(f"### Total Chunks: {total_chunks}")

    # Select Chunk to Process
    chunk_index = st.number_input("Select Chunk Index", min_value=0, max_value=total_chunks - 1, value=0, step=1)
    chunk_data = data.iloc[chunk_index * chunk_size:(chunk_index + 1) * chunk_size]
    st.write("### Current Chunk:")
    st.write(chunk_data)

    if st.button("Generate Bios for Current Chunk"):
        # Add Generated Bios to Data
        chunk_data["Bio"] = chunk_data.apply(generate_bio, axis=1)
        st.write("### Generated Bios:")
        st.write(chunk_data[["Name", "University", "Bio"]])

        # Download Option
        csv = chunk_data.to_csv(index=False)
        st.download_button(
            label="Download Current Chunk as CSV",
            data=csv,
            file_name=f"chunk_{chunk_index}_bios.csv",
            mime="text/csv"
        )
    st.info("Use the Chunk Index to process the next set of rows.")

# Internet Search Section
st.write("### Search Profiles on the Internet")
full_name = st.text_input("Full Name (First and Last)", help="Enter the full name of the academic.")
university = st.text_input("University", help="Enter the university name.")
research_interest = st.text_input("Research Interest", help="Enter a research or teaching interest.")

if st.button("Search on Internet"):
    if "serper_api_key" in st.secrets:
        result = search_internet(full_name, university, research_interest)
        st.write("### Internet Search Results:")
        st.write(result)
    else:
        st.warning("Serper API Key is missing in Streamlit Secrets.")
