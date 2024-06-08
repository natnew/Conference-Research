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

# Retrieve the OpenAI API key from the secrets file
openai_api_key = st.secrets["openai_api_key"]

# Define example templates
templates = {
    "Formal": "Subject: Connect prior to the conference at the University of Warwick\n\nDear [Name],\n\nI am writing to you on behalf of [Your Name] from [Your Institution/Company]. We are interested in connecting with Asma Abdi, who is a postdoctoral fellow at the University of Warwick's Institute of Advanced Study. ...",
    "Motivated": "Subject: Excited to Connect at the University of Warwick Conference\n\nDear [Name],\n\nI hope this message finds you well. My name is [Your Name], and I represent [Your Institution/Company]. We have been following Asma Abdi's impactful research at the University of Warwick, and we are eager to explore potential collaborations...",
    "Informal": "Subject: Let's Connect at the Warwick Conference!\n\nHi [Name],\n\nI hope you're doing well! I'm [Your Name] from [Your Institution/Company]. I've heard great things about Asma Abdi's work at the University of Warwick, and I think it would be fantastic to meet up and chat about possible collaborations...",
    "Disappointed": "Subject: Follow-up on Previous Outreach\n\nDear [Name],\n\nI hope this message finds you well. I am [Your Name] from [Your Institution/Company]. We had previously reached out to connect with Asma Abdi from the University of Warwick regarding her research, but we haven't heard back. We are still very interested...",
    "Casual": "Subject: Quick Chat at the Conference?\n\nHey [Name],\n\nI'm [Your Name] from [Your Institution/Company]. I came across Asma Abdi's research at the University of Warwick, and I thought it would be great to connect during the upcoming conference. Let me know if you're free to meet up for a quick chat!",
    "Example 1": "Dear Dr/Professor XX,\n\nI hope this message finds you well. I’m writing to ask if we could arrange to meet during the ISA conference this April? I’ll be in San Francisco and would love to offer you a coffee or to meet in the Exhibitors’ Hall for a quick discussion about a new textbook idea.\n\nI am the Politics editor here at Sage and would find it invaluable to have an opportunity to discuss your teaching of (and research interests in) XXX. I appreciate a textbook may (or may not…) be something you have considered working on in the near future, but I’d also love a quick, open and exploratory discussion about texts, your experience using existing books, and an idea I have for a new textbook in a little more detail.\n\nI’d be delighted if we could meet at the Sage stand during ISA. Looking at my diary, I could meet between 8am and 5pm on any day during the conference: Wednesday April 3rd, Thursday 4th and Friday 5th. I’m also available between 9am and 1pm on Saturday April 6th. I hope we might have chance to meet at the ISA, and look forward to hearing from you.\n\nWith best wishes,\nAndrew",
    "Example 2": "Dear Dr/Professor XX,\n\nI hope this message finds you well. I’m writing to ask if we could arrange to meet during the PSA conference in late March? I’ll be in Glasgow and would love to offer you a coffee or to meet at the Sage stand for a quick discussion about a new textbook idea.\n\nI am the Politics editor here at Sage and would find it invaluable to have an opportunity to discuss your teaching of (and research interests in) XXX. I appreciate a textbook may (or may not…) be something you have considered working on in the near future, but I’d also love a quick, open and exploratory discussion about texts, your experience using existing books, and an idea I have for a new textbook in a little more detail.\n\nI’d be delighted if we could meet at the Sage stand during PSA. Looking at my diary, I could meet any time between 8am and 5:30pm on Monday, March 25th and Tuesday 26th and between 8am and 2pm on Wednesday, March 27th. I hope we might have chance to meet at the PSA, and look forward to hearing from you.\n\nWith best wishes,\nAndrew"
}

def generate_response(input_text):
    # Initialize the OpenAI LLM with the API key
    llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)
    # Generate the response and display it in the app
    st.info(llm(input_text))

# Create a form for user input
with st.form('my_form'):
    # Dropdown for selecting a template
    template_choice = st.selectbox('Choose a template:', list(templates.keys()))
    # Text area for user input
    text = st.text_area('Enter text:', templates[template_choice])
    # Create a submit button
    submitted = st.form_submit_button('Submit')
    
    # Check if the API key is valid
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    
    # If the form is submitted and the API key is valid, generate the response
    if submitted and openai_api_key.startswith('sk-'):
        generate_response(text)
