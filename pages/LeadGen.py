import os
import openai
import streamlit as st

with st.sidebar:
    st.markdown("# About")
    st.markdown(
       "A collection of Multi AI Agent Systems "
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    openai_api_key = st.text_input("OpenAI API Key", key="file_qa_api_key", type="password")
    "[View the source code](https://github.com/natnew/Conference-Research/RAG.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Lead Generation")


