import streamlit as st
import pandas as pd
from con_research.src.modules.scrapping_module import ContentScraper
from con_research.src.modules.search_module import SerperDevTool

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

# Internet Search Function
def search_internet(full_name, university, serper_api_key):
    """
    Search for academic profiles on the internet using the Serper API.
    Extract research interests, teaching interests, published papers, and contact details.
    """
    query = (
        f'"{full_name}" "{university}" "research interests" '
        f'"teaching interests" "academic papers" "contact details"'
    )
    tool = SerperDevTool(api_key=serper_api_key)
    search_results = tool._run(query)

    # Combine relevant content from search results
    bio_content = ""
    for url in search_results:
        content = ContentScraper.scrape_anything(url)
        bio_content += content + "\n\n"
    
    return bio_content if bio_content else "No relevant information found online."

st.title("BioGen - Automated Bio Generator")

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

    # Check if required columns are present
    required_columns = ['Name', 'University']
    if all(col in data.columns for col in required_columns):
        st.success("File contains the required columns for processing.")

        # Add a placeholder for the Bio column if not already present
        if 'Bio' not in data.columns:
            data['Bio'] = ""

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
            serper_api_key = st.secrets["serper_api_key"]  # Access API key from secrets
            
            # Iterate through each row in the chunk
            for index, row in chunk_data.iterrows():
                full_name = row['Name']
                university = row['University']

                # Search internet for bio content
                bio_content = search_internet(full_name, university, serper_api_key)
                data.at[index, 'Bio'] = bio_content  # Update the bio column

            # Display Updated Chunk
            updated_chunk = data.iloc[chunk_index * chunk_size:(chunk_index + 1) * chunk_size]
            st.write("### Updated Chunk with Bios:")
            st.write(updated_chunk)

            # Download Option
            csv = updated_chunk.to_csv(index=False)
            st.download_button(
                label="Download Current Chunk as CSV",
                data=csv,
                file_name=f"chunk_{chunk_index}_bios.csv",
                mime="text/csv"
            )
        st.info("Use the Chunk Index to process the next set of rows.")
    else:
        st.error(f"Uploaded file must contain the following columns: {required_columns}")
