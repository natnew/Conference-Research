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
    openai_api_key = st.secrets["openai_api_key"]

# Main App Title and Description
st.title("💬 Outreach - Email Generation")
st.markdown("Craft emails to participants to reach out and engage with them before the conference. :balloon:")

# -----------------------------------------------
# Template setup and state management
# -----------------------------------------------
templates = {
    "Custom": "",
    "Template 1": (
        "Dear Dr/Professor [NAME],\n"
        "I hope this message finds you well. I’m writing to ask if we could arrange to meet during the [CONFERENCE NAME] conference in late [DATE]? I’ll be in [CITY] and would love to offer you a coffee or to meet at the Sage stand for a quick discussion about a new textbook idea.\n\n"
        "I am the [TOPIC] editor here at Sage and would find it invaluable to have an opportunity to discuss your teaching of (and research interests in) [TOPIC]. I appreciate a textbook may (or may not…) be something you have considered working on in the near future, but I’d also love a quick, open and exploratory discussion about texts, your experience using existing books, and an idea I have for a new textbook in a little more detail.\n\n"
        "I’d be delighted if we could meet at the Sage stand during [CONFERENCE NAME]. Looking at my diary, I could meet any time between [TIME] on [DAY], [MONTH] and [TIME] on [DAY], [MONTH]. I hope we might have chance to meet at the [CONFERENCE NAME], and look forward to hearing from you.\n\n"
        "With best wishes,\n\n[YOUR NAME]"
    ),
}

if "email_text" not in st.session_state:
    st.session_state.email_text = templates["Template 1"]
if "template_choice" not in st.session_state:
    st.session_state.template_choice = "Template 1"
if "enhanced_email" not in st.session_state:
    st.session_state.enhanced_email = ""

def update_template():
    template_text = templates.get(st.session_state.template_choice, "")
    if template_text:
        st.session_state.email_text = template_text


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
        st.session_state.enhanced_email = response
    except Exception as e:
        st.error(f"Error generating response: {e}")

# Template selector
st.selectbox(
    'Select a template:',
    options=list(templates.keys()),
    key='template_choice',
    on_change=update_template,
)

# Form for User Input
with st.form('email_form'):
    email_text = st.text_area(
        'Enter your email draft:',
        value=st.session_state.email_text,
        key='email_text'
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

# Display enhanced email for editing and copying
if st.session_state.enhanced_email:
    st.markdown("**Enhanced Email:**")
    st.text_area(
        label="", key="enhanced_email", height=200
    )
    if st.button('Copy Enhanced Email'):
        st.code(st.session_state.enhanced_email, language=None)
