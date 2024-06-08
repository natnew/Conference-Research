import streamlit as st
from langchain.llms import OpenAI

with st.sidebar:
    st.markdown("# About")
    st.markdown(
       "We use multi-agent systems and other AI technologies to power this app."
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    openai_api_key = st.secrets["openai_api_key"]
    "[View the source code](https://github.com/natnew/Conference-Research/RAG.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Outreach - Email Generation")
st.markdown("Craft emails to participants to reach out and engage with them before the conference.")


# Retrieve the OpenAI API key from the secrets file
openai_api_key = st.secrets["openai_api_key"]

def generate_response(input_text):
    # Initialize the OpenAI LLM with the API key
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    # Generate the response and display it in the app
    st.info(llm(input_text))

# Create a form for user input
with st.form('my_form'):
    # Create a text area for user input
    text = st.text_area('Enter text:', 'What are the three key pieces of advice for learning how to code?')
    # Create a submit button
    submitted = st.form_submit_button('Submit')
    
    # Check if the API key is valid
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    
    # If the form is submitted and the API key is valid, generate the response
    if submitted and openai_api_key.startswith('sk-'):
        generate_response(text)
