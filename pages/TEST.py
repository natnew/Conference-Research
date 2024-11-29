import streamlit as st
from openai import OpenAI  # Ensure this is properly imported
import pandas as pd
from io import BytesIO

# Load the Chat API key from Streamlit secrets
openai.api_key = st.secrets["openai_api_key"]


# Helper function to generate bio using OpenAI client
def generate_bio(name, university):
    prompt = (
        f"Generate a professional bio for {name}, who is affiliated with {university}. "
        "Include their research interests, teaching interests, any paper titles they may have published, "
        "and contact information such as email or LinkedIn."
    )
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=st.secrets["openai_api_key"])

        # Initialize session state for messages if not already done
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Add the user prompt to session state
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        # Generate response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=st.session_state.messages
        )
        msg = response.choices[0].message.content

        # Add the assistant's response to session state
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

        return msg
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
    
    data = []
    invalid_lines = []
    
    for line in lines:
        parts = line.split(",", 1)  # Split into at most two parts
        if len(parts) == 2:
            name, university = parts
            data.append({"Name": name.strip(), "University": university.strip()})
        else:
            invalid_lines.append(line)

    if invalid_lines:
        st.warning("Some lines were ignored due to invalid format:")
        for line in invalid_lines:
            st.text(f"- {line}")
    
    if data:
        # Display a scrollable table for the parsed data
        st.write("### Names and Universities Found in the File:")
        st.dataframe(pd.DataFrame(data))  # Display as a scrollable table

        # Batch processing
        batch_size = st.number_input("Number of rows to process in each batch", min_value=1, max_value=len(data), value=10)
        total_batches = (len(data) + batch_size - 1) // batch_size
        st.write(f"### Total Batches: {total_batches}")

        # Select current batch
        batch_index = st.number_input("Select Batch Index", min_value=0, max_value=total_batches - 1, value=0)

        # Extract current batch
        start_idx = batch_index * batch_size
        end_idx = min(start_idx + batch_size, len(data))
        current_batch = data[start_idx:end_idx]

        st.write(f"### Processing Batch {batch_index + 1}/{total_batches}")
        st.dataframe(pd.DataFrame(current_batch))

        # Generate bios for the current batch
        if st.button("Generate Bios for Current Batch"):
            st.write("Generating bios for the current batch...")
            bios = []
            for entry in current_batch:
                name = entry["Name"]
                university = entry["University"]
                st.write(f"Generating bio for {name} ({university})...")
                bio = generate_bio(name, university)
                bios.append({"Name": name, "University": university, "Bio": bio})

            # Convert to DataFrame
            df = pd.DataFrame(bios)

            # Convert DataFrame to Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name=f"Bios_Batch_{batch_index + 1}")
            output.seek(0)

            # Provide download link
            st.download_button(
                label=f"Download Batch {batch_index + 1} as Excel",
                data=output,
                file_name=f"academic_bios_batch_{batch_index + 1}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.info("Use the Batch Index to process other batches sequentially.")
    else:
        st.error("No valid entries found in the file. Make sure each line contains a name and a university separated by a comma.")
