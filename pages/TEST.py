import streamlit as st
import pandas as pd
import requests
import openai
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

# Google Custom Search API Function
def google_search(query, google_cse_id, google_api_key):
    """
    Perform a search using Google Custom Search JSON API.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,  # Search query
        "cx": google_cse_id,  # Custom Search Engine ID
        "key": google_api_key,  # Google API Key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

# OpenAI Summarization Function
def summarize_bio(content, openai_api_key):
    """
    Use OpenAI's API to summarize the extracted content into a bio.
    """
    openai.api_key = openai_api_key
    prompt = f"Summarize the following information into a concise academic bio:\n\n{content}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        temperature=0.7,
    )
    return response["choices"][0]["text"].strip()

# Internet Search Function
def search_and_generate_bio(full_name, university, serper_api_key, google_cse_id, google_api_key, openai_api_key):
    """
    Use Serper API, Google Custom Search API, and OpenAI API to generate a short bio.
    """
    # Query Google Custom Search API
    google_results = google_search(f"{full_name} {university}", google_cse_id, google_api_key)
    google_content = "\n".join(
        [f"{item['title']} - {item['snippet']}" for item in google_results.get("items", [])]
    )

    # Query Serper API
    serper_tool = SerperDevTool(api_key=serper_api_key)
    serper_results = serper_tool._run(f"{full_name} {university} research teaching")

    # Scrape content from Serper results
    serper_content = ""
    for url in serper_results:
        try:
            serper_content += ContentScraper.scrape_anything(url) + "\n\n"
        except Exception as e:
            serper_content += f"Failed to scrape {url}: {str(e)}\n\n"

    # Combine content and summarize using OpenAI
    combined_content = f"{google_content}\n{serper_content}"
    bio = summarize_bio(combined_content, openai_api_key)
    return bio

# Streamlit App Title
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
            # Access API keys from Streamlit secrets
            serper_api_key = st.secrets.get("serper_api_key")
            google_cse_id = st.secrets.get("google_cse_id")
            google_api_key = st.secrets.get("google_api_key")
            openai_api_key = st.secrets.get("openai_api_key")

            if not (serper_api_key and google_cse_id and google_api_key and openai_api_key):
                st.error("One or more API keys are missing. Please add them to the secrets file.")
            else:
                # Iterate through each row in the chunk
                for index, row in chunk_data.iterrows():
                    full_name = row['Name']
                    university = row['University']

                    # Search and generate bio content
                    bio_content = search_and_generate_bio(
                        full_name, university,
                        serper_api_key, google_cse_id, google_api_key, openai_api_key
                    )
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
