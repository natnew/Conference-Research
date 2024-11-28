import streamlit as st
import pandas as pd
from openai import OpenAI
from con_research.src.modules.scrapping_module import ContentScraper
from con_research.src.modules.search_module import SerperDevTool

# Set API Keys from Streamlit Secrets
openai.api_key = st.secrets["openai_api_key"]

# Internet Scraping Function
def scrape_for_missing_data(name, university):
    """
    Scrape the internet for missing information.
    """
    query = f"{name} {university} academic profile"
    tool = SerperDevTool(api_key=st.secrets["serper_api_key"])
    search_results = tool._run(query)
    if search_results:
        content = ContentScraper.scrape_anything(search_results[0])
        return content
    return None

# GPT API Function
def generate_bio(name, university, research_interest, teaching_interest):
    """
    Generate a professional bio using GPT-3.5-turbo.
    """
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": (
            f"Generate a professional bio for {name}, an academic affiliated with {university}. "
            f"Their research interests include {research_interest}, and they teach {teaching_interest}."
        )}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()


# Bio Generation Function
def generate_bio(row):
    """
    Generate a bio for a given row, using scraping and GPT for missing data.
    """
    name = row.get('Name', 'N/A')
    profession = row.get('Profession', 'N/A')
    specialization = row.get('Specialization', 'N/A')
    university = row.get('University', 'N/A')
    research_interest = row.get('Research Interest', 'N/A')
    teaching_interest = row.get('Teaching Interest', 'N/A')
    contact_details = row.get('Contact Details', 'N/A')

    # Scrape or Generate Missing Data
    if profession == 'N/A' or specialization == 'N/A':
        scraped_data = scrape_for_missing_data(name, university)
        if scraped_data:
            specialization = specialization if specialization != 'N/A' else "from scraping: " + scraped_data

    if profession == 'N/A':
        profession = generate_from_gpt(name, university, research_interest, teaching_interest)

    return (f"{name} is a {profession} specializing in {specialization}, currently affiliated with {university}. "
            f"Their research interests include {research_interest}, and they are passionate about teaching {teaching_interest}. "
            f"You can reach out to them at {contact_details}.")

# Streamlit App Configuration
st.title("BioGen - Advanced Bio Generator with Scraping and GPT")
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
        st.write(chunk_data[["Name", "University", "Bio"]])

        # Download Option
        csv = chunk_data.to_csv(index=False)
        st.download_button(
            label="Download Current Chunk as CSV",
            data=csv,
            file_name=f"chunk_{chunk_index}_bios.csv",
            mime="text/csv"
        )
    st.info("Use the Chunk Index to process the next set of rows.")
