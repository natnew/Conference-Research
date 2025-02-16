import streamlit as st
from openai import OpenAI
import pandas as pd
import os
import tiktoken
import PyPDF2  # <-- for PDF processing

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

with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
       "We use multi-agent systems and other AI technologies to power this app."
    )
    st.markdown(
       "This tool is a work in progress."
    )
    openai_api_key = st.secrets["openai_api_key"]
   
st.title("💬 RAG - Lead Generation")
st.markdown("Search and Filter Conference Participants: Retrieve Relevant Information Based on University Affiliation and Year, Including Research and Teaching Areas. :balloon:")

uploaded_file = st.file_uploader("Upload an article", type=("txt", "md", "xlsx", "pdf"))
question = st.text_input(
    "Ask something about the article",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

########
# Function to estimate tokens
def estimate_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 uses this encoding
    tokens = len(encoding.encode(text))
    return tokens

def extract_text_from_pdf(file):
    """
    Extract all text from a PDF using PyPDF2.
    """
    pdf_reader = PyPDF2.PdfReader(file)
    all_text = []
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page_text = page.extract_text()
        if page_text:
            all_text.append(page_text)
    return "\n".join(all_text)

article = None

if uploaded_file:
    if uploaded_file.name.endswith('.txt') or uploaded_file.name.endswith('.md'):
        # Read text content
        try:
            article = uploaded_file.read().decode('utf-8')
        except UnicodeDecodeError:
            st.error("Could not decode the text file. Please ensure it's UTF-8 or ISO-8859-1.")
            article = None

    elif uploaded_file.name.endswith('.xlsx'):
        # Read Excel content
        df = pd.read_excel(uploaded_file)
        article = df.to_string(index=False)

    elif uploaded_file.name.endswith('.pdf'):
        # Parse PDF content
        try:
            article = extract_text_from_pdf(uploaded_file)
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            article = None

    else:
        st.error("Unsupported file type.")
        article = None

    if article:
        # Estimate tokens
        total_tokens = estimate_tokens(article) + estimate_tokens(question)
        st.markdown(f"**Estimated Token Count:** {total_tokens}")

        # Warn if token count is too high
        if total_tokens > 9000:  # threshold for GPT-4 context limit
            st.warning(
                "The input size is too large and may exceed token limits. "
                "Consider reducing the file size or summarising the content."
            )

        if question and total_tokens <= 9000:
            st.success("Input is within acceptable token limits. Ready to process!")

########

# Process the uploaded file and question
if uploaded_file and question and not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")

if uploaded_file and question and openai_api_key and article:
    try:
        # Prepare the prompt for OpenAI API
        prompt = f"Here's an article:\n\n{article}\n\nQuestion: {question}\nAnswer:"
        
        # Set OpenAI API key
        os.environ['OPENAI_API_KEY'] = openai_api_key
        client = OpenAI(api_key=openai_api_key)

        # Call OpenAI API to get the response
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0,
        )

        # Display the response
        st.write("### Answer")
        st.write(response.choices[0].message.content.strip())

    except Exception as e:
        st.error(f"An error occurred: {e}")
