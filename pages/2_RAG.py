from openai import OpenAI
import streamlit as st

with st.sidebar:
    st.markdown("# About")
    st.markdown(
       "We use multi-agent systems and other AI technologies to power this app. "
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    openai_api_key = st.secrets["openai_api_key"]
    "[View the source code](https://github.com/natnew/Conference-Research/RAG.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 RAG")
st.markdown("Search database")

uploaded_file = st.file_uploader("Upload an article", type=("txt", "md", "xlsx"))
question = st.text_input(
    "Ask something about the article",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and question and not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")

if article:
    # Prepare the prompt for OpenAI API
    prompt = f"Here's an article:\n\n{article}\n\nQuestion: {question}\nAnswer:"
            

    # Set OpenAI API key
    openai.api_key = openai_api_key

    # Call OpenAI API to get the response
    response = openai.Completion.create(
        engine="gpt-4",  # Use GPT-4 model
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0,
    )

    st.write("### Answer")
    st.write(response.completion)
