import streamlit as st
import openai
import pandas as pd
from io import BytesIO

# Load the Chat API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

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

# Upload the text file
st.title("Academic Bio Generator")
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
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No valid entries found in the file. Make sure each line contains a name and a university separated by a comma.")
