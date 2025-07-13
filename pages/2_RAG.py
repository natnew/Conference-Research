import streamlit as st
from openai import OpenAI
import pandas as pd
import os
import tiktoken
import PyPDF2
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

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
    st.markdown("We use multi-agent systems and other AI technologies to power this app.")
    st.markdown("This tool is a work in progress.")
    st.page_link("pages/1_About.py", label="About", icon="ℹ️")
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
        # Estimate tokens of the full article plus the question
        total_tokens = estimate_tokens(article) + estimate_tokens(question)
        st.markdown(f"**Estimated Token Count:** {total_tokens}")

        # Warn if token count is too high
        if total_tokens > 9000:  # threshold for GPT-4 context limit
            st.warning(
                "The input size is too large and may exceed token limits. "
                "The text will be chunked for retrieval."
            )
        else:
            st.success("Input is within acceptable token limits.")

########

# Process the uploaded file and question with LangChain-style chunking and retrieval
if uploaded_file and question and openai_api_key and article:
    try:
        # Step 1: Chunk the article text into manageable pieces
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_text(article)
        st.write(f"Text has been split into {len(chunks)} chunks.")

        # Step 2: Create embeddings and build a FAISS vector store
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        vectorstore = FAISS.from_texts(chunks, embeddings)
        st.info("Embeddings created and vector store built.")

        # Step 3: Set up the retrieval chain using GPT-4 as the language model
        chat_llm = ChatOpenAI(model_name="gpt-4", openai_api_key=openai_api_key)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=chat_llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
        )

        # Step 4: Process the question using the retrieval chain
        with st.spinner("Querying the document..."):
            result = qa_chain({"query": question})

        # Step 5: Display the answer and source documents
        st.write("### Answer")
        st.write(result["result"])
        st.write("---")
        st.write("### Source Documents (Extracts)")
        for i, doc in enumerate(result["source_documents"]):
            st.write(f"**Document {i+1}:**")
            st.write(doc.page_content[:500] + "...")
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
elif uploaded_file and question and not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
