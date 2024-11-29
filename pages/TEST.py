import streamlit as st
import openai
import pandas as pd
from io import BytesIO

# Load the Chat API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]

# Helper function to generate bio using ChatGPT API
def generate_bio(name, university):
    prompt = (
        f"Generate a professional bio for {name}, who is affiliated with {university}. "
        "Include their research interests, teaching interests, any paper titles they may have published, "
        "and contact information such as email or LinkedIn."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.7,
        )
        bio = response.choices[0].message["content"]
        return bio
    except Exception as e:
        return f"Error generating bio: {e}"

# App title
st.title("Academic Bio Generator")

# Section 1: Excel to TXT conversion
st.header("Step 1: Convert Excel to TXT")
excel_file = st.file_uploader("Upload an Excel file with 'Name' and 'University' columns", type="xlsx")

if excel_file:
    # Read Excel file
    df_excel = pd.read_excel(excel_file)

    # Validate column names
    if "Name" in df_excel.columns and "University" in df_excel.columns:
        st.write("Excel file preview:")
        st.dataframe(df_excel)

        # Convert to TXT format
        txt_data = "\n".join(f"{row['Name']}, {row['University']}" for _, row in df_excel.iterrows())
        txt_bytes = txt_data.encode("utf-8")

        # Provide download link for TXT file
        st.download_button(
            label="Download as TXT",
            data=txt_bytes,
            file_name="names_and_universities.txt",
            mime="text/plain"
        )
    else:
        st.error("The Excel file must have 'Name' and 'University' columns.")

# Section 2: Generate bios from TXT
st.header("Step 2: Generate Bios from TXT")
uploaded_file = st.file_uploader("Upload a text file containing names and universities (one per line)", type="txt")

if uploaded_file:
    # Read the uploaded file
    content = uploaded_file.read().decode("utf-8")
    lines = content.strip().split("\n")
    data = [line.split(",") for line in lines if "," in line]  # Expecting "Name, University" format

    if data:
        st.write("Names and Universities found in the file:")
        for name, university in data:
            st.write(f"- {name} ({university})")
        
        # Generate bios
        st.write("Generating bios...")
        bios = []
        for name, university in data:
            st.write(f"Generating bio for {name} ({university})...")
            bio = generate_bio(name.strip(), university.strip())
            bios.append({"Name": name.strip(), "University": university.strip(), "Bio": bio})
        
        # Convert to DataFrame
        df = pd.DataFrame(bios)

        # Convert DataFrame to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Bios")
        output.seek(0)

        # Provide download link
        st.download_button(
            label="Download Bios as Excel",
            data=output,
            file_name="academic_bios.xlsx",
            mi
