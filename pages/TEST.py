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
def search_internet(full_name, university, research_interest, serper_api_key):
    """
    Search for academic profiles on the internet using the Serper API.
    """
    query = f"{full_name} {university} {research_interest} academic research"
    
    # Use SerperDevTool for web scraping and searching
    tool = SerperDevTool(api_key=serper_api_key)
    search_results = tool._run(query)

    bio_content = ""
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        bio_content += content + "\n"
    
    return bio_content if bio_content else "No relevant web results found."

# API Key Input
serper_api_key = st.sidebar.text_input("Enter Serper API Key", type="password", help="Required for internet searches.")

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
    re
