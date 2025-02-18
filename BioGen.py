import streamlit as st
import pandas as pd
import openai
import re
from openai import OpenAI  
#from con_research.src.modules.scrapping_module import ContentScraper
#from con_research.src.modules.search_module import SerperDevTool
from duckduckgo_search import DDGS  

# Sidebar Configuration
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content
and assists in lead generation. Designed to support academic and professional
activities, it offers interconnected modules that streamline research tasks,
whether for conferences, campus visits, or other events.
""")

st.sidebar.write(
    "Built by [Natasha Newbold](https://www.linkedin.com/in/natasha-newbold/) "
)

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This app leverages cutting-edge technologies to automate and enhance research
    workflows. It combines generative AI, voice-to-action capabilities,
    Retrieval-Augmented Generation (RAG), agentic RAG, and other advanced
    methodologies to deliver efficient and accurate results.
    """)

# Additional Information in the Sidebar
with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "Search for academic profiles by querying local files (CSV/XLSX) or the internet. Combine the power of local data and web scraping to uncover detailed academic profiles. "
    )
    st.markdown("This tool is a work in progress.")
    openai_api_key = st.secrets["openai_api_key"]

# Updated Bio Generation Function
def generate_bio_with_chatgpt(full_name, university):
    """
    Generate a bio using OpenAI's ChatGPT API.
    """
    prompt = (
        f"Generate a professional bio for {full_name}, who is affiliated with {university}. "
        "Include their research interests, teaching interests, any paper titles they may have published, "
        "and contact information such as email."
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
        st.error(f"Error generating bio with ChatGPT: {e}")
        return None

def fallback_generate_bio_with_ddgs(full_name, university):
    """
    Fallback mechanism to generate a bio using DuckDuckGo search.
    """
    prompt = (
        f"Generate a professional bio for {full_name}, who is affiliated with {university}. "
        "Include their research interests, teaching interests, any paper titles they may have published, "
        "and contact information such as email. In your response just provide the bio text response don't begin with `Below is a sample professional bio`"
    )
    try:
        results = DDGS().chat(prompt, model='gpt-4o-mini',timeout: int = 100)
        return results
    except Exception as e:
        st.error(f"Error generating bio with DuckDuckGo: {e}")
        return None

# Updated Internet Search Function
def search_internet_with_chatgpt(full_name, university):
    """
    Use ChatGPT to generate a bio if scraping or search results are unavailable.
    """
    # Combine internet scraping (if needed) with ChatGPT bio generation
    bio_content = generate_bio_with_chatgpt(full_name, university)
    if not bio_content:
        st.warning("Falling back to DuckDuckGo search for bio generation.")
        bio_content = fallback_generate_bio_with_ddgs(full_name, university)
    return bio_content

# App Title
st.title("BioGen - Automated Bio Generator")

# File Upload
uploaded_file = st.file_uploader("Upload your CSV/XLSX file :balloon:", type=["csv", "xlsx"])
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
        if 'Email' not in data.columns:
            data['Email'] = ""

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
            # Iterate through each row in the chunk
            for index, row in chunk_data.iterrows():
                full_name = row['Name']
                university = row['University']

                # Generate bio using ChatGPT
                # bio_content = search_internet_with_chatgpt(full_name, university)
                bio_content = fallback_generate_bio_with_ddgs(full_name, university)
                data.at[index, 'Bio'] = bio_content  # Update the bio column

                # Extract email from the bio content (if applicable)
                email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", bio_content)
                email_address = email_match.group() if email_match else "Email not found"

                # Update the DataFrame
                data.at[index, 'Bio'] = bio_content
                data.at[index, 'Email'] = email_address

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
