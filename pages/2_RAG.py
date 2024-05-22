import streamlit as st
import openai

with st.sidebar:
    st.markdown("# About")
    st.markdown(
       "We use multi-agent systems and other AI technologies to power this app."
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    openai_api_key = st.text_input("OpenAI API Key", key="file_qa_api_key", type="password")
    "[View the source code](https://github.com/natnew/Conference-Research/RAG.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 RAG")
st.markdown("Search and Filter Conference Participants: Retrieve Relevant Information Based on University Affiliation and Year, Including Research and Teaching Areas")
uploaded_file = st.file_uploader("Upload an article", type=("txt", "md", "xlsx"))
question = st.text_input(
    "Ask something about the article",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and question and not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")

if uploaded_file and question and openai_api_key:
    article = uploaded_file.read().decode()
    prompt = f"Here's an article:\n\n{article}\n\nQuestion: {question}\nAnswer:"

    openai.api_key = openai_api_key
    response = openai.Completion.create(
        engine="gpt-4",  # Use GPT-4 model
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7,
    )
    st.write("### Answer")
    st.write(response.choices[0].text.strip())
