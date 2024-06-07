import streamlit as st
from openai import OpenAI
import os

# Load OpenAI API key from cloud secrets
openai_api_key = os.getenv("OPENAI_API_KEY")

with st.sidebar:
    st.markdown("# About")

# Upload file and question inputs
uploaded_file = st.file_uploader("Choose a file")
question = st.text_input("Enter your question")

# Process the uploaded file and question
if uploaded_file and question:
    try:
        if uploaded_file.name.endswith('.txt') or uploaded_file.name.endswith('.md'):
            # Attempt to read the file with UTF-8 encoding
            article = uploaded_file.read().decode('utf-8')
            st.write("### Article Content")
            st.write(article)  # Display the article content for debugging

            prompt = f"Here's an article:\n\n{article}\n\nQuestion: {question}\nAnswer:"

            # Set OpenAI API key
            openai.api_key = openai_api_key
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

            # Check the response
            if response and response.choices:
                answer = response.choices[0].message['content'].strip()
                st.write("### Answer")
                st.write(answer)
            else:
                st.write("No response received from the OpenAI API.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error(f"Details: {str(e)}")

            
