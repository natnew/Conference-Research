import streamlit as st
from openai import OpenAI
import pandas as pd
import os

# Sidebar
with st.sidebar:
    st.markdown("# About")

# Main app
st.title("File and Question Processor")

# File upload
uploaded_file = st.file_uploader("Choose a file", type=["txt", "md"])

# Question input
question = st.text_input("Enter your question")

# Set OpenAI API key
openai_api_key = st.secrets["openai_api_key"]
openai.api_key = openai_api_key
os.environ['openai_api_key'] = openai_api_key
client = OpenAI(api_key=openai_api_key)

# Process the uploaded file and question
if uploaded_file and question:
    try:
        if uploaded_file.name.endswith('.txt') or uploaded_file.name.endswith('.md'):
            # Attempt to read the file with UTF-8 encoding
            article = uploaded_file.read().decode('utf-8')

            prompt = f"Here's an article:\n\n{article}\n\nQuestion: {question}\nAnswer:"

            # Call OpenAI API to get the response
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=100,
                n=1,
                stop=None,
                temperature=0,
            )

            # Display the response
            st.write("### Answer")
            st.write(response.choices[0].message["content"].strip())
    except Exception as e:
        st.error(f"An error occurred: {e}")
