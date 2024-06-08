import streamlit as st
from langchain.llms import OpenAI

# Sidebar information
with st.sidebar:
    st.markdown("# About")
    st.markdown(
        "We use multi-agent systems and other AI technologies to power this app."
    )
    st.markdown(
        "This tool is a work in progress."
    )
    openai_api_key = st.secrets["openai_api_key"]
    st.markdown("[View the source code](https://github.com/natnew/Conference-Research/RAG.py)")
    st.markdown("[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)")

st.title("💬 Lead Generation")
st.markdown("Craft emails to participants to reach out and engage with them before the conference.")

def generate_response(input_text):
  llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
  st.info(llm(input_text))

with st.form('my_form'):
  text = st.text_area('Enter text:', 'What are the three key pieces of advice for learning how to code?')
  submitted = st.form_submit_button('Submit')
  if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
  if submitted and openai_api_key.startswith('sk-'):
    generate_response(text)
