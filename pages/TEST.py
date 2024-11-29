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
st.title("Academic Bio Generator with Batch Processing")

# Step 1: Upload TXT File
uploaded_file = st.file_uploader("Upload a text file containing names and universities (one per line)", type="txt")

if uploaded_file:
    # Read and process the TXT file
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

    # Warn about invalid lines
    if invalid_lines:
        st.warning("Some lines were ignored due to invalid format:")
        for line in invalid_lines:
            st.text(f"- {line}")
    
    # If valid data exists, proceed
    if data:
        # Display total rows and allow batch processing
        df = pd.DataFrame(data)
        total_rows = len(df)
        
        st.success(f"File contains {total_rows} rows.")
        
        # Select batch size
        batch_size = st.number_input("Number of rows per chunk", min_value=1, max_value=total_rows, value=10, step=1)
        
        # Calculate number of chunks
        total_chunks = (total_rows + batch_size - 1) // batch_size
        st.write(f"### Total Chunks: {total_chunks}")
        
        # Select chunk index
        chunk_index = st.number_input("Select Chunk Index", min_value=0, max_value=total_chunks - 1, value=0, step=1)
        
        # Extract current chunk
        start_idx = chunk_index * batch_size
        end_idx = min(start_idx + batch_size, total_rows)
        current_chunk = df.iloc[start_idx:end_idx].copy()
        
        st.write("### Current Chunk:")
        st.dataframe(current_chunk)
        
        # Add column for generated bios
        if st.button("Generate Bios for Current Chunk"):
            st.write("Generating bios...")
            current_chunk["Bio"] = current_chunk.apply(
                lambda row: generate_bio(row["Name"], row["University"]), axis=1
            )
            st.success("Bios generated successfully!")
            
            # Display updated chunk with bios
            st.write("### Updated Chunk with Bios:")
            st.dataframe(current_chunk)
            
            # Save the current chunk to a downloadable file
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                current_chunk.to_excel(writer, index=False, sheet_name="Bios")
            output.seek(0)
            
            # Provide download link
            st.download_button(
                label="Download Current Chunk as Excel",
                data=output,
                file_name=f"bios_chunk_{chunk_index + 1}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.info("Use the Chunk Index to process the next set of rows.")
    else:
        st.error("No valid entries found in the file. Make sure each line contains a name and a university separated by a comma.")
