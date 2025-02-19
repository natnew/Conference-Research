import streamlit as st
import pandas as pd
import openai
import re
from openai import OpenAI
from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup
import tiktoken
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# Function to scrape text from a URL
def scrape_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        response.encoding = 'utf-8'  # Specify the encoding
        try:
            soup = BeautifulSoup(response.content, 'html.parser')  # You can also try 'lxml' or 'html5lib'
            # Extract text from paragraphs and other relevant tags
            paragraphs = soup.find_all(['p', 'li', 'span', 'div'])
            text = ' '.join([para.get_text() for para in paragraphs])
        except Exception as e:
            print(f"Error parsing {url} with BeautifulSoup: {e}")
            text = response.text  # Fall back to raw text content
        return text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to clean and organize text
def clean_text(text):
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# Function to truncate text to fit within token limit
def truncate_text(text, max_tokens, encoding_name="cl100k_base"):
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    truncated_tokens = tokens[:max_tokens]
    truncated_text = encoding.decode(truncated_tokens)
    return truncated_text

# Function to generate enriched text using DDGS
def generate_enriched_text(full_name, university):
    query = f"a professional bio and email for {full_name}, who is affiliated with {university}."
    results = DDGS().text(query, max_results=3)

    enriched_text = ""
    for result in results:
        url = result['href']
        body_text = result['body']
        scraped_text = scrape_text_from_url(url)
        if scraped_text is not None:
            combined_text = f"{body_text} {scraped_text}"
            enriched_text += clean_text(combined_text) + " "
        else:
            enriched_text += clean_text(body_text) + " "

    # Format the enriched text into a block of text
    enriched_text = re.sub(r'\s+', ' ', enriched_text).strip()
    return enriched_text

# Function to generate bio using ChatGPT
def generate_bio_with_chatgpt(full_name, university, truncated_text):
    prompt = (
        f"Create a professional biographical profile for {full_name}, who is affiliated with {university}, based on the following information: {truncated_text}\n\n"
        "Important guidelines:\n"
        "1. Do NOT assume any titles (like Dr. or Professor) unless explicitly mentioned in the provided information\n"
        "2. Only include factual information that is directly supported by the provided text\n"
        "3. Format the bio in the following structure:\n"
           "- Full name and current position (exactly as provided)\n"
           "- Institutional affiliations\n"
           "- Email address (if available)\n"
           "- Research focus and interests\n"
           "- Teaching activities (if any)\n"
           "- Notable publications or projects (only if specifically mentioned)\n"
        "4. If certain information is not available in the provided text, omit that section rather than making assumptions\n"
        "5. Keep the tone professional but factual, avoiding speculative or honorary language"
    )
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=st.secrets["openai_api_key"])

        # Generate response
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}]
        )
        results = response.choices[0].message.content

        return results
    except Exception as e:
        st.error(f"Error generating bio with ChatGPT: {e}")
        return None

# Function to extract email from bio content
def extract_email(bio_content):
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", bio_content)
    return email_match.group() if email_match else "Email not found"

# Function to process a single row
def process_row(index, row):
    full_name = row['Name']
    university = row['University']

    # Generate enriched text using DDGS
    enriched_text = generate_enriched_text(full_name, university)

    # Truncate enriched text to fit within token limit
    max_tokens = 100000  # Adjust this value based on your model's token limit
    truncated_text = truncate_text(enriched_text, max_tokens)

    # Generate bio using ChatGPT
    bio_content = generate_bio_with_chatgpt(full_name, university, truncated_text)
    if bio_content:
        # Extract email from the bio content
        email_address = extract_email(bio_content)
        return index, bio_content, email_address
    return index, None, None

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
            # Process rows in parallel
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(process_row, index, row) for index, row in chunk_data.iterrows()]
                for future in as_completed(futures):
                    index, bio_content, email_address = future.result()
                    if bio_content:
                        data.at[index, 'Bio'] = bio_content  # Update the bio column
                        data.at[index, 'Email'] = email_address

            # Display Updated Chunk
            updated_chunk = data.iloc[chunk_index * chunk_size:(chunk_index + 1) * chunk_size]
            st.write("### Updated Chunk with Bios:")
            st.write(updated_chunk)

            # Download Option
            output = BytesIO()
            updated_chunk.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            st.download_button(
                label="Download Current Chunk as CSV",
                data=output,
                file_name=f"chunk_{chunk_index}_bios.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.info("Use the Chunk Index to process the next set of rows.")
    else:
        st.error(f"Uploaded file must contain the following columns: {required_columns}")
