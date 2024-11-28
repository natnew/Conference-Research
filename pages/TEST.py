import streamlit as st
import pandas as pd

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

st.title("BioGen - Chunk-Based Bio Generator")

# Helper Function for Bio Generation
def generate_bio(row):
    """
    Generate a bio for a given row of data.
    """
    name = row.get('Name', 'N/A')
    profession = row.get('Profession', 'N/A')
    specialization = row.get('Specialization', 'N/A')
    return f"{name} is a {profession} specializing in {specialization}."

# File Upload
uploaded_file = st.file_uploader("Upload your CSV/XLSX file", type=["csv", "xlsx"])
if uploaded_file:
    # Load File
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.write("### File Preview:")
    st.write(data.head())

    # Specify Chunk Size
    chunk_size = st.number_input("Number of rows per chunk", min_value=1, max_value=len(data), value=10)
    total_chunks = (len(data) + chunk_size - 1) // chunk_size
    st.write(f"### Total Chunks: {total_chunks}")

    # Select Chunk to Process
    chunk_index = st.number_input("Select Chunk Index", min_value=0, max_value=total_chunks - 1, value=0, step=1)
    chunk_data = data.iloc[chunk_index * chunk_size:(chunk_index + 1) * chunk_size]
    st.write("### Current Chunk:")
    st.write(chunk_data)

    if st.button("Generate Bios for Current Chunk"):
        # Add Generated Bios to Data
        chunk_data["Bio"] = chunk_data.apply(generate_bio, axis=1)
        st.write("### Generated Bios:")
        st.write(chunk_data[["Name", "Bio"]])

        # Download Option
        csv = chunk_data.to_csv(index=False)
        st.download_button(
            label="Download Current Chunk as CSV",
            data=csv,
            file_name=f"chunk_{chunk_index}_bios.csv",
            mime="text/csv"
        )
    st.info("Use the Chunk Index to process the next set of rows.")
