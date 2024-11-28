import streamlit as st
from openai import OpenAI
import pandas as pd
import os

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


with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
       "We use multi-agent systems and other AI technologies to power this app."
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    openai_api_key = st.secrets["openai_api_key"]
   

st.title("💬 RAG - Lead Generation")
st.markdown("Search and Filter Conference Participants: Retrieve Relevant Information Based on University Affiliation and Year, Including Research and Teaching Areas. :balloon:")
uploaded_file = st.file_uploader("Upload an article", type=("txt", "md", "xlsx"))
question = st.text_input(
    "Ask something about the article",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)


# Process the uploaded file and question
if uploaded_file and question and not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")

if uploaded_file and question and openai_api_key:
    try:
        if uploaded_file.name.endswith('.txt') or uploaded_file.name.endswith('.md'):
            # Attempt to read the file with UTF-8 encoding
            try:
                article = uploaded_file.read().decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # If UTF-8 fails, attempt to read the file with a different encoding, e.g., ISO-8859-1
                    article = uploaded_file.read().decode('ISO-8859-1')
                except UnicodeDecodeError:
                    # If all attempts fail, handle the error (e.g., display an error message to the user)
                    st.error("The uploaded file has an unsupported encoding. Please upload a file with UTF-8 or ISO-8859-1 encoding.")
                    article = None
        elif uploaded_file.name.endswith('.xlsx'):
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            article = df.to_string(index=False)  # Convert DataFrame to string
        else:
            st.error("Unsupported file type.")
            article = None

        if article:
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
                stop=None,
                temperature=0,
            )

            # Display the response
            st.write("### Answer")
            st.write(response.choices[0].message.content.strip())

    except Exception as e:
        st.error(f"An error occurred: {e}")
