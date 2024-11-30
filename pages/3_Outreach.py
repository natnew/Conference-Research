import streamlit as st
from langchain.llms import OpenAI
import streamlit.components.v1 as components




st.sidebar.title("Conference Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content 
and assists in lead generation. Designed to support academic and professional 
activities, it offers interconnected modules that streamline research tasks, 
whether for conferences, campus visits, or other events.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This app leverages cutting-edge technologies to automate and enhance research 
    workflows. It combines generative AI, voice-to-action capabilities, 
    Retrieval-Augmented Generation (RAG), agentic RAG, and other advanced 
    methodologies to deliver efficient and accurate results.

    """)

# Sidebar information
with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "We use multi-agent systems and other AI technologies to power this app."
    )
    st.markdown(
        "This tool is a work in progress."
    )
    openai_api_key = st.secrets["openai_api_key"]
    

st.title("💬 Outreach - Email Generation")
st.markdown("Craft emails to participants to reach out and engage with them before the conference. :balloon:")

def generate_response(input_text):
    try:
        llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        response = llm(input_text)
        st.info(response)
    except Exception as e:
        st.error(f"Error generating response: {e}")

with st.form('my_form'):
    text = st.text_area('Enter text:', 'Craft emails to participants to reach out and engage with them before the conference.')
    submitted = st.form_submit_button('Submit')
    
    if submitted:
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
        else:
            generate_response(text)

