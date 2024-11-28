import streamlit as st
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import requests
import openai

# Set OpenAI API Key
openai.api_key = st.secrets["openai_api_key"]

# Function to search the internet using Google Custom Search API
def search_internet(query, google_api_key, google_cse_id):
    try:
        service = build("customsearch", "v1", developerKey=google_api_key)
        results = service.cse().list(q=query, cx=google_cse_id, num=3).execute().get("items", [])
        return [item['link'] for item in results]
    except Exception as e:
        return []

# Function to scrape content from a URL
def scrape_content(url):
    try:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        driver.get(url)
        time.sleep(3)
        content = driver.find_element(By.TAG_NAME, "body").text
        driver.quit()
        return content
    except Exception as e:
        return f"Failed to scrape content from {url}: {e}"

# Function to generate a short bio using OpenAI
def generate_bio(content):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Generate a concise academic bio (under 100 words) from the following content:\n\n{content}",
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Failed to generate bio: {e}"

# Streamlit app starts here
st.title("Bio Generator for Conference Speakers")

uploaded_file = st.file_uploader("Upload your Excel file with 'Name' and 'University' columns", type=["xlsx"])
if uploaded_file:
    # Load the file and preview the data
    data = pd.read_excel(uploaded_file)
    st.write("### File Preview:")
    st.write(data.head())

    # Validate columns
    if 'Name' in data.columns and 'University' in data.columns:
        st.success("File contains the required columns for processing.")
    else:
        st.error("The file must contain 'Name' and 'University' columns.")
        st.stop()

    # Add a 'Bio' column if it doesn't exist
    if 'Bio' not in data.columns:
        data['Bio'] = ""

    # Batch size selection
    batch_size = st.number_input("Number of rows per batch", min_value=1, max_value=len(data), value=10)
    total_batches = (len(data) + batch_size - 1) // batch_size
    st.write(f"### Total Batches: {total_batches}")

    # Button to process the current batch
    if st.button("Generate Bios for Current Batch"):
        google_api_key = st.secrets["google_api_key"]
        google_cse_id = st.secrets["google_cse_id"]

        # Process each row in the current batch
        for index, row in data.iterrows():
            if pd.isna(row['Bio']):  # Skip rows with existing bios
                query = f"{row['Name']} {row['University']}"
                urls = search_internet(query, google_api_key, google_cse_id)

                # Scrape content from URLs
                bio_content = ""
                for url in urls:
                    bio_content += scrape_content(url) + "\n\n"

                # Generate bio using OpenAI
                data.at[index, 'Bio'] = generate_bio(bio_content)

        # Show updated data
        st.write("### Updated Data:")
        st.write(data)

        # Allow download of results
        output_file = data.to_csv(index=False)
        st.download_button(
            label="Download Results",
            data=output_file,
            file_name="bios_generated.csv",
            mime="text/csv"
        )

