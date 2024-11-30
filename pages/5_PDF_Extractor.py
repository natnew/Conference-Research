import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import re
from io import BytesIO

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
       "Extract names, universities, and other relevant details from uploaded PDFs. Use this tool to analyze documents quickly and efficiently."
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    openai_api_key = st.secrets["openai_api_key"]

# Function to clean and normalize text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces/newlines with single space
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)  # Fix hyphenated words split across lines
    text = text.replace('  ', ' ')  # Extra clean-up for double spaces
    return text

# Function to extract names and universities from text
def extract_names_and_universities(text):
    name_univ_pattern = r"([A-Z][a-z]+ [A-Z][a-z]+)\s+\(([^\)]+University[^\)]*)\)"  # Match names and universities
    matches = re.findall(name_univ_pattern, text)
    return pd.DataFrame(matches, columns=["Name", "University"]) if matches else pd.DataFrame(columns=["Name", "University"])

# Streamlit App UI
st.title("PDF Extractor - Names and Universities")
st.write("Upload a PDF file, extract and clean its text, and find names and universities. :balloon:")

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Processing the PDF..."):
        try:
            # Extract text from PDF
            reader = PdfReader(uploaded_file)
            raw_text = ""
            for page in reader.pages:
                raw_text += page.extract_text()

            # Show raw extracted text for debugging
            st.write("### Raw Extracted Text")
            st.text_area("Raw Text", raw_text, height=300)

            # Clean and normalize the text
            cleaned_text = clean_text(raw_text)
            st.write("### Cleaned Text")
            st.text_area("Cleaned Text", cleaned_text, height=300)

            # Extract names and universities
            df = extract_names_and_universities(cleaned_text)

            if not df.empty:
                st.success("Extraction completed!")
                st.write("### Extracted Names and Universities")
                st.dataframe(df)

                # Download as Excel
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                st.download_button(
                    label="Download Extracted Data as Excel",
                    data=output,
                    file_name="extracted_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            else:
                st.warning("No names or universities were found in the cleaned text.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
