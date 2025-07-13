import streamlit as st
from langchain.llms import OpenAI

# Sidebar Configuration
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
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
    st.markdown("We use multi-agent systems and other AI technologies to power this app.")
    st.markdown("This tool is a work in progress.")
    st.page_link("pages/1_About.py", label="About", icon="ℹ️")
    openai_api_key = st.secrets["openai_api_key"]

# Main App Title and Description
st.title("💬 Outreach - Email Generation")
st.markdown("Craft emails to participants to reach out and engage with them before the conference. :balloon:")

def generate_response(original_text, tone, length):
    prompt = f"""
    Please enhance the following email. 
    Use a {tone.lower()} tone and ensure the email is {length.lower()} in length.
    
    Original Email:
    {original_text}
    
    Enhanced Email:
    """
    try:
        llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
        response = llm(prompt)
        st.info(response)
    except Exception as e:
        st.error(f"Error generating response: {e}")

# Form for User Input
with st.form('email_form'):
    email_text = st.text_area(
        'Enter your email draft:', 
        'Dear [Name],\n\nI hope this message finds you well. I am reaching out to invite you to our upcoming conference...'
    )
    tone = st.selectbox(
        'Select the tone of the email:',
        options=['Formal', 'Casual', 'Friendly', 'Professional']
    )
    length = st.selectbox(
        'Select the desired length of the email:',
        options=['Short', 'Medium', 'Long']
    )
    enhance = st.form_submit_button('Enhance')
    
    if enhance:
        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
        else:
            generate_response(email_text, tone, length)
