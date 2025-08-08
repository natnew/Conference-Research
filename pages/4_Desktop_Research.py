"""
Desktop Research - Academic Profile Search Module
================================================

A Streamlit tool for comprehensive academic profile searches using local data files and
AI-generated biographical content. Facilitates academic networking by providing detailed
researcher information through intelligent data processing.

KEY FEATURES:
- Local file search (CSV/XLSX) with real-time filtering
- AI-powered biography generation using OpenAI GPT models
- Academic profile synthesis including research/teaching interests
- Contact information extraction and export capabilities

REQUIREMENTS:
- openai_api_key: OpenAI API key
- Dependencies: streamlit, pandas, openai, re
- Input: CSV/XLSX files with Name, University/Affiliation columns

WORKFLOW:
1. Upload data files → 2. Search/filter by name/institution/research area
3. Select individuals → 4. AI generates comprehensive profiles → 5. Export results

AI BIOGRAPHY INCLUDES:
- Academic background and current position
- Research interests and teaching responsibilities
- Publications and contact information

USE CASES:
- Pre-conference research and academic collaboration discovery
- Research interest mapping and contact compilation for outreach
"""

import streamlit as st
import pandas as pd
import re
from openai import OpenAI


# Sidebar Configuration
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content 
and assists in lead generation. Designed to support academic and professional 
activities, it offers interconnected modules that streamline research tasks, 
whether for conferences, campus visits, or other events.
""")

# Additional Sidebar Info
with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "Search for academic profiles by querying local files (CSV/XLSX) or the internet. Combine the power of local data and AI-generated bios to uncover detailed academic profiles."
    )
    st.markdown("This tool is a work in progress.")
    openai_api_key = st.secrets.get("openai_api_key")
    if not openai_api_key:
        st.warning("OpenAI key is not configured. Some features may be disabled.")

def generate_bio_with_chatgpt(researcher_full_name, university_affiliation):
    """
    Generates a concise academic biography using OpenAI GPT-4o-mini for desktop research purposes.
    
    Args:
        researcher_full_name (str): Complete name of the academic researcher
        university_affiliation (str): Institutional affiliation for context
        
    Returns:
        str: Brief academic biography (typically 100-200 words) focusing on research areas,
             key achievements, and institutional role
             
    Raises:
        openai.OpenAIError: If API key is invalid or request fails
        Exception: If response generation fails
        
    Dependencies:
        - Requires valid OpenAI API key in st.secrets["openai_api_key"]
        - Uses GPT-4o-mini-2024-07-18 model
        
    Note:
        Generates shorter biographies compared to main BioGen module.
        Designed for quick desktop research and overview generation.
        Does not include web search enrichment for faster processing.
    """
    """
    Generate a professional bio using OpenAI's ChatGPT API.
    """
    prompt = (
        f"Generate a professional bio for {researcher_full_name}, who is affiliated with {university_affiliation}. "
        "Include their research interests, teaching interests, any paper titles they may have published, "
        "and contact information such as email."
    )
    try:
        # Initialize the OpenAI client
        openai_client = OpenAI(api_key=openai_api_key)

        # Generate response
        chat_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        return f"Error generating bio: {e}"

def main():
    """
    Main execution function for the Desktop Research Streamlit application interface.
    
    Functionality:
        - Renders Streamlit UI components for researcher input
        - Handles user form submission and validation
        - Coordinates biography generation workflow
        - Manages session state and error handling
        - Displays results and download options
        
    Side Effects:
        - Updates Streamlit session state variables
        - Renders UI components and user feedback
        - Handles file downloads and data persistence
        
    Note:
        Entry point for the desktop research page. Manages the complete user interaction
        flow from input collection to result display and export functionality.
    """
    st.title("Desktop Research")
    st.markdown("Search for academic profiles by querying local files (CSV/XLSX) or the internet. :balloon:")

    # User Input Fields
    researcher_full_name = st.text_input("Full Name (First and Last Name)")
    university_affiliation = st.text_input("University")
    search_scope = st.selectbox("Where would you like to search?", ["Local Files", "Internet", "Both"])

    # Optional File Upload
    uploaded_datasets = st.file_uploader("Upload CSV/XLSX files (optional for local search)", type=["csv", "xlsx"], accept_multiple_files=True)

    if st.button("Search"):
        if search_scope == "Internet":
            # Internet Search with ChatGPT
            if researcher_full_name and university_affiliation:
                st.write("### Generating Bio with AI...")
                bio_content = generate_bio_with_chatgpt(researcher_full_name, university_affiliation)
                st.write("### Bio Content:")
                st.write(bio_content)

                # Extract Email
                email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", bio_content)
                extracted_email_address = email_match.group() if email_match else "Email not found"
                st.write(f"### Extracted Email: {extracted_email_address}")
            else:
                st.error("Please provide both Full Name and University.")

        if search_scope in ["Local Files", "Both"]:
            # Process Local File Search
            if uploaded_datasets:
                st.write("### Searching in Local Files...")
                for dataset_file in uploaded_datasets:
                    if dataset_file.name.endswith(".csv"):
                        file_dataframe = pd.read_csv(dataset_file)
                    else:
                        file_dataframe = pd.read_excel(dataset_file)

                    st.write("### File Preview:")
                    st.write(file_dataframe.head())

                    # If 'University' column is missing but 'Affiliation' exists, rename it
                    if 'University' not in file_dataframe.columns and 'Affiliation' in file_dataframe.columns:
                        file_dataframe.rename(columns={'Affiliation': 'University'}, inplace=True)
                        st.info("'Affiliation' column found and renamed to 'University' for processing.")

                    # Check required columns
                    if 'Name' in file_dataframe.columns and 'University' in file_dataframe.columns:
                        st.success("File contains required columns.")
                        file_dataframe['Bio'] = file_dataframe.apply(
                            lambda row: generate_bio_with_chatgpt(row['Name'], row['University']), axis=1
                        )
                        st.write("### Updated Data:")
                        st.write(file_dataframe)

                        # Download Option
                        csv_export = file_dataframe.to_csv(index=False)
                        st.download_button(
                            label="Download Updated File",
                            data=csv_export,
                            file_name="updated_data_with_bios.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error("Uploaded file must contain 'Name' and 'University' columns.")
            else:
                st.warning("Please upload a file to search in local data.")

# Run the App
if __name__ == "__main__":
    main()
