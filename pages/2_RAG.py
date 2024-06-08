import streamlit as st
import openai
import pandas as pd
import os

# Streamlit web app
st.sidebar.markdown("About")
st.title("This tool is a work in progress.")

openai_api_key = os.getenv("OPENAI_API_KEY")

uploaded_file = st.file_uploader("Choose a file")
question = st.text_input("Ask a question")

if uploaded_file and question:
    # Process the uploaded file and question
    if not openai_api_key:
        st.warning("Please add your OpenAI API key to continue.")

    try:
        # Try to read the file with utf-8 encoding
        article = uploaded_file.read().decode('utf-8')
    except UnicodeDecodeError:
        try:
            # If utf-8 fails, attempt to read the file with a different encoding, e.g., ISO-8859-1
            article = uploaded_file.read().decode('ISO-8859-1')
        except UnicodeDecodeError:
            # If all decoding attempts fail, handle the error (e.g., display an error message to the user)
            st.error("Unsupported file type. The file has an unsupported encoding. Please upload a file with UTF-8 or ISO-8859-1 encoding.")
            article = None

    if article:
        # Convert DataFrame to string if needed
        if isinstance(article, pd.DataFrame):
            article = article.to_string(index=False)

        # Prepare the prompt for OpenAI API
        prompt = f"Here is an article:\n\n{article}\n\nQuestion: {question}\n\nAnswer:"

        # Send request to OpenAI API
        if openai_api_key:
            openai.api_key = openai_api_key
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=300,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )

                # Display the response
                answer = response.choices[0].message['content'].strip()
                st.write(answer)
            except Exception as e:
                st.error(f"An error occurred: {e}")
else:
    st.write("Please upload a file and ask a question.")
