"""
PDF Extractor - Intelligent Document Analysis Module
===================================================

A Streamlit PDF processing tool using AI-powered extraction to identify and structure
academic information from conference proceedings, participant lists, and institutional
documents. Automatically extracts names, affiliations, and locations from PDFs.

KEY FEATURES:
- Advanced PDF text extraction using PyMuPDF and pymupdf4llm
- AI-powered entity recognition with Pydantic validation
- Parallel processing for large document batches
- Intelligent name/affiliation detection and Excel export

REQUIREMENTS:
- openai_api_key: OpenAI API key
- Dependencies: streamlit, pandas, pydantic, openai, fitz, pymupdf4llm, concurrent.futures
- Input: Text-based PDFs (not image-only scans)

WORKFLOW:
1. Upload PDFs → 2. Process and convert to text → 3. AI analyzes and extracts entities
4. Validate with Pydantic models → 5. Review results → 6. Export to Excel

EXTRACTION MODELS:
- ExtractedInfo: name, university, location
- ExtractionResponse: List of all identified individuals
- CorrectionResponse: Error validation and correction

USE CASES:
- Conference participant extraction and academic collaboration analysis
- Author affiliation processing and contact database creation
"""

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
    location: Optional[str] = Field(None, description="The country location of the university.")

class ExtractionResponse(BaseModel):
    extracted_info: List[ExtractedInfo]

class CorrectionResponse(BaseModel):
    corrected_info: List[ExtractedInfo]
# for page in range(total_pages)
# Function to extract text from PDF using pymupdf4llm
def extract_text_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    total_pages = pdf_document.page_count
    page_texts = []

    for page_number in range(total_pages):
        markdown_text = pymupdf4llm.to_markdown(pdf_path, pages=[page_number])
        page_texts.append(markdown_text)

    pdf_document.close()
    return page_texts

# Function to extract information using LLM
def extract_info_with_llm(document_text, openai_client):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {"role": "system", "content": """Extract names, universities, and locations from the provided text if there is no location infer it from your general knowledge of where the university is located but just give the country name of the location don't include the city. 
            Ensure the data you provide is accurate, clean of any weird character in the names try to reconstruct them to the best of your capabilities, and verifiable with the source provided.
            If you cannot infer the location just leave it empty."""},
            {"role": "user", "content": document_text}
        ],
        response_format=ExtractionResponse
    )
    api_response_data = response.choices[0].message.content
    parsed_extraction_data = json.loads(api_response_data)
    return parsed_extraction_data.get("extracted_info", [])

# Function to correct extracted information using LLM
def correct_info_with_llm(raw_extracted_data, source_text, openai_client):
    correction_prompt = """ Review and clean the extracted information below against the source text.

                            EXTRACTED DATA:
                            {raw_extracted_data}
                            
                            SOURCE TEXT:
                            {source_text}
                            
                            INSTRUCTIONS:
                            1. Verify names and universities against the source text only
                            2. Clean ALL special characters and symbols from names:
                               - Remove or replace characters: [], {}, /, \, ?, *, ', :, =, +, -, ~, !, @, #, $, %, ^, &, (, )
                               - Keep only alphanumeric characters, spaces, and standard punctuation (., ,)
                               - Example: "John D. Smith" is valid, "John (D.) Smith!" is not
                            3. Use official university names when identifiable
                            4. If the information is not present in the source text leave the field  empty
                            5. Do not modify or verify inferred locations
                            6. Ensure all text values are Excel-safe (no illegal worksheet characters)
                            
                            VALIDATION RULES:
                            1. Field Emptiness:
                               - Replace any "N/A", "null", "none", "unknown", "-" with empty string ("")
                               - Remove any entries where name is empty but other fields have values
                               - If name is not in text, remove the entire entry
                            
                            2. Location Handling:
                               - If location contains placeholder values (N/A, null, none, unknown, etc.), replace with empty string
                               - Keep only valid location values that were previously inferred
                            
                            3. Logical Consistency:
                               - Each entry MUST have a name to be valid
                               - Entries without names should be removed entirely
                               - University can be empty if not mentioned
                               - Location can be empty if not previously inferred
                            """
    #correction_prompt = f"Correct and clean the following extracted information:\n{extracted_data}\n\nBased on the original text:\n{text}\n\nEnsure the formatting is accurate and the information is complete, correct and gotten rid of weird characters, and verifiable with the source. Note that the locations provided are inferred from general knowledge so no need to verify that, only focus on the name and the university while some names have been constructed because they might have had weird characters.In your output when verifying if something is not mentioned in the text just leave it empty don't fill it with not mentioned in the text."
    response = openai_client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are a corrector. Correct and clean the extracted information based on the original text."},
            {"role": "user", "content": correction_prompt}
        ],
        response_format=CorrectionResponse
    )
    correction_response = response.choices[0].message.content
    parsed_correction_data = json.loads(correction_response)
    return parsed_correction_data.get("corrected_info", [])

# Streamlit App UI
st.title("PDF Extractor - Names, Universities, and Locations")
st.write("Upload a PDF file, extract and clean its text, and find names, universities, and locations. :balloon:")

# Initialize session state
if 'extracted_dataframe' not in st.session_state:
    st.session_state.extracted_dataframe = pd.DataFrame()
if 'extraction_done' not in st.session_state:
    st.session_state.extraction_done = False

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None and not st.session_state.extraction_done:
    with st.spinner("Processing the PDF..."):
        try:
            # Extract text from PDF
            pdf_bytes = uploaded_file.getvalue()
            with open("temp.pdf", "wb") as temp_pdf_file:
                temp_pdf_file.write(pdf_bytes)

            page_texts = extract_text_from_pdf("temp.pdf")
            openai_client = OpenAI(api_key=openai_api_key)

            all_raw_extractions = []

            # Use ThreadPoolExecutor for parallel processing
            with ThreadPoolExecutor(max_workers=10) as executor:
                extraction_futures = [executor.submit(extract_info_with_llm, page_text, openai_client) for page_text in page_texts]
                for future in extraction_futures:
                    page_extracted_data = future.result()
                    all_raw_extractions.extend(page_extracted_data)

            # Use ThreadPoolExecutor for parallel processing of correction
            final_corrected_data = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                correction_futures = [executor.submit(correct_info_with_llm, extraction_item, page_texts[0], openai_client) for extraction_item in all_raw_extractions]
                for future in correction_futures:
                    corrected_entries = future.result()
                    final_corrected_data.extend(corrected_entries)

            # Convert to DataFrame and remove duplicates
            results_dataframe = pd.DataFrame(final_corrected_data)
            results_dataframe.drop_duplicates(inplace=True)

            # Store DataFrame in session state
            st.session_state.extracted_dataframe = results_dataframe
            st.session_state.extraction_done = True

            if not results_dataframe.empty:
                st.success("Extraction completed!")
                st.write("### Extracted Names, Universities, and Locations")
                st.dataframe(results_dataframe)

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Check if DataFrame exists in session state
if 'extracted_dataframe' in st.session_state and not st.session_state.extracted_dataframe.empty:
    # Filtering by location
    st.write("### Filter by Location")
    available_locations = st.session_state.extracted_dataframe['location'].dropna().unique()
    selected_locations = st.multiselect("Select locations to filter", available_locations)

    if selected_locations:
        location_filtered_dataframe = st.session_state.extracted_dataframe[st.session_state.extracted_dataframe['location'].isin(selected_locations)]
        st.write("### Filtered DataFrame")
        st.dataframe(location_filtered_dataframe)

        # Download as Excel
        filtered_excel_output = BytesIO()
        location_filtered_dataframe.to_excel(filtered_excel_output, index=False, engine='openpyxl')
        filtered_excel_output.seek(0)
        st.download_button(
            label="Download Filtered Data as Excel",
            data=filtered_excel_output,
            file_name="filtered_names_and_university_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.warning("Please select at least one location to filter the data.")

    # Download original DataFrame as Excel
    original_excel_output = BytesIO()
    st.session_state.extracted_dataframe.to_excel(original_excel_output, index=False, engine='openpyxl')
    original_excel_output.seek(0)
    st.download_button(
        label="Download Original Data as Excel",
        data=original_excel_output,
        file_name="original_names_and_university_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
