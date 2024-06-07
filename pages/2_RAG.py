import streamlit as st
from openai import OpenAI
import pandas as pd
import os

with st.sidebar:
    st.markdown("# About")

# Upload file and question inputs
uploaded_file = st.file_uploader("Choose a file")
question = st.text_input("Enter your question")
openai_api_key = st.text_input("Enter your OpenAI API key", type="password")

# Process the uploaded file and question
if uploaded_file and question:
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    else:
        try:
            if uploaded_file.name.endswith('.txt') or uploaded_file.name.endswith('.md'):
                # Attempt to read the file with UTF-8 encoding
                article = uploaded_file.read().decode('utf-8')

                prompt = f"Here's an article:\n\n{article}\n\nQuestion: {question}\nAnswer:"

                # Set OpenAI API key
                openai.api_key = openai_api_key
                os.environ['OPENAI_API_KEY'] = openai_api_key
                client = OpenAI(api_key=openai_api_key)

                # Call OpenAI API to get the response
                response = client.chat.completions.create(
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
                st.write(response.choices[0].message['content'].strip())

        except Exception as e:
            st.error(f"An error occurred: {e}")
