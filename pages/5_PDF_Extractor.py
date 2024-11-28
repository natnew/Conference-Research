import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
import re
from io import BytesIO

# Function to extract names and universities from the PDF
def extract_names_and_universities(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    # Regex to find names and universities (simplified example, adjust based on your PDF structure)
    name_univ_pattern = r"([A-Z][a-z]+ [A-Z][a-z]+)\s+(\bUniversity\b.*)"
    matches = re.findall(name_univ_pattern, text)
    
    # Create a DataFrame
    data = {"Name": [], "University": []}
    for match in matches:
        data["Name"].append(match[0])
        data["University"].append(match[1])
    
    return pd.DataFrame(data)

# Streamlit UI
st.title("PDF Extractor - Names and Universities")
st.write("Upload a PDF file to extract names and associated universities. You can view and download the extracted data.")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Processing the PDF..."):
        try:
            # Extract data from PDF
            df = extract_names_and_universities(uploaded_file)
            
            if not df.empty:
                st.success("Extraction completed!")
                # Display the extracted data
                st.write("### Extracted Data")
                st.dataframe(df)
                
                # Download button
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
                st.warning("No names or universities were found in the uploaded PDF. Please try again with a different file.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
