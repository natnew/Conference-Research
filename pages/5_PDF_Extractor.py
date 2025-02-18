import streamlit as st
import pandas as pd
import re
from io import BytesIO
from pydantic import BaseModel, Field
from typing import List, Optional
from openai import OpenAI
import fitz  # PyMuPDF
import pymupdf4llm
import json
from concurrent.futures import ThreadPoolExecutor

# Sidebar content
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
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
        "This tool is a work in progress."
    )
    openai_api_key = st.secrets["openai_api_key"]

# Pydantic model for LLM response
class ExtractedInfo(BaseModel):
    name: str = Field(..., description="The name of the individual.")
    university: str = Field(..., description="The name of the university.")
    location: Optional[str] = Field(None, description="The location of the university.")

class ExtractionResponse(BaseModel):
    extracted_info: List[ExtractedInfo]

# Function to extract text from PDF using pymupdf4llm
def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    total_pages = pdf_document.page_count
    pages_to_process = [0, 1, 2, 3, 4, 5]
    extracted_texts = []

    for page in pages_to_process:
        md_text = pymupdf4llm.to_markdown(pdf_path, pages=[page])
        extracted_texts.append(md_text)

    pdf_document.close()
    return extracted_texts

# Function to extract information using LLM
def extract_info_with_llm(text, openai_client):
    response = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": "Extract names, universities, and locations from the provided text if their is no location infer it from your general knowledge of where the university is located."},
            {"role": "user", "content": text}
        ],
        response_format=ExtractionResponse
    )
    extracted_data = response.choices[0].message.content
    extracted_data_parsed = json.loads(extracted_data)
    return extracted_data_parsed.get("extracted_info", [])

# Streamlit App UI
st.title("PDF Extractor - Names, Universities, and Locations")
st.write("Upload a PDF file, extract and clean its text, and find names, universities, and locations. :balloon:")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Processing the PDF..."):
        try:
            # Extract text from PDF
            pdf_bytes = uploaded_file.getvalue()
            with open("temp.pdf", "wb") as temp_pdf:
                temp_pdf.write(pdf_bytes)

            extracted_texts = extract_text_from_pdf("temp.pdf")
            openai_client = OpenAI(api_key=openai_api_key)

            all_extracted_data = []

            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(extract_info_with_llm, text, openai_client) for text in extracted_texts]
                for future in futures:
                    extracted_data = future.result()
                    all_extracted_data.extend(extracted_data)

            # Convert to DataFrame and remove duplicates
            df = pd.DataFrame(all_extracted_data)
            df.drop_duplicates(inplace=True)

            # Store DataFrame in session state
            st.session_state.df = df

            if not df.empty:
                st.success("Extraction completed!")
                st.write("### Extracted Names, Universities, and Locations")
                st.dataframe(df)

# Filtering by location
st.write("### Filter by Location")
available_locations = st.session_state.df['location'].dropna().unique()
selected_locations = st.multiselect("Select locations to filter", available_locations)

if selected_locations:
    filtered_df = st.session_state.df[st.session_state.df['location'].isin(selected_locations)]
    st.write("### Filtered DataFrame")
    st.dataframe(filtered_df)

    # Download as Excel
    output = BytesIO()
    filtered_df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    st.download_button(
        label="Download Filtered Data as Excel",
        data=output,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.warning("Please select at least one location to filter the data.")
