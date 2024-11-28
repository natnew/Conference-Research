import os
import pandas as pd
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
import streamlit as st

# App Sidebar Configuration
st.sidebar.title("Conference Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content 
and assists in lead generation. Designed to support academic and professional 
activities, it offers interconnected modules that streamline research tasks, 
whether for conferences, campus visits, or other events.
""")

with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This app leverages cutting-edge technologies to automate and enhance research 
    workflows. It combines generative AI, voice-to-action capabilities, 
    Retrieval-Augmented Generation (RAG), agentic RAG, and other advanced 
    methodologies to deliver efficient and accurate results.
    """)

# Configure API keys
serper_api_key = os.getenv("SERPER_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set up OpenAI Chat Model (LangChain)
chat_model = ChatOpenAI(
    model="gpt-3.5-turbo",  # Use "gpt-4" if available
    temperature=0.7,
    openai_api_key=openai_api_key
)

# Set up Serper Tool for Search
serper_tool = SerperDevTool(api_key=serper_api_key)

# Function to Scrape Websites (Optional)
scrape_tool = ScrapeWebsiteTool()

# Function to Query Serper API
def search_with_serper(query: str):
    """
    Use Serper API to perform a web search.
    """
    results = serper_tool._run(query)
    return results

# Function to Summarize Results Using OpenAI Chat
def summarize_content(content: str) -> str:
    """
    Summarize raw search content into a concise academic bio using OpenAI ChatCompletion.
    """
    # LangChain Chat Prompt
    prompt = ChatPromptTemplate.from_template(
        "You are an assistant that generates concise academic bios. Summarize the following information into a short bio:\n\n{content}"
    )
    # Format prompt
    messages = prompt.format_messages(content=content)
    
    # Generate response
    response = chat_model(messages)
    return response.content.strip()

# Full Bio Generation Function
def generate_bio(name: str, university: str) -> str:
    """
    Generate a bio by combining Serper search results and OpenAI summarization.
    """
    # Query Serper API
    query = f"{name} {university} research interests, academic papers, contact details"
    search_results = search_with_serper(query)
    
    if not search_results:
        return "No relevant information found."

    # Combine results into a single text for summarization
    combined_content = ""
    for url in search_results:
        try:
            scraped_content = scrape_tool._run(url)
            combined_content += scraped_content + "\n\n"
        except Exception as e:
            combined_content += f"Failed to scrape {url}: {str(e)}\n\n"

    # Summarize using OpenAI Chat
    return summarize_content(combined_content)

# Streamlit App Title
st.title("LangChain-Powered Bio Generator")

uploaded_file = st.file_uploader("Upload your CSV/XLSX file", type=["csv", "xlsx"])
if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.write("### File Preview:")
    st.write(data.head())

    # Check required columns
    required_columns = ['Name', 'University']
    if all(col in data.columns for col in required_columns):
        st.success("File contains the required columns for processing.")

        # Add Bio column if not present
        if 'Bio' not in data.columns:
            data['Bio'] = ""

        # Chunk size input
        chunk_size = st.number_input("Number of rows per chunk", min_value=1, max_value=len(data), value=10)
        total_chunks = (len(data) + chunk_size - 1) // chunk_size
        st.write(f"### Total Chunks: {total_chunks}")

        # Select chunk to process
        chunk_index = st.number_input("Select Chunk Index", min_value=0, max_value=total_chunks - 1, value=0, step=1)
        chunk_data = data.iloc[chunk_index * chunk_size:(chunk_index + 1) * chunk_size]
        st.write("### Current Chunk:")
        st.write(chunk_data)

        if st.button("Generate Bios for Current Chunk"):
            # Iterate through each row and generate bios
            for index, row in chunk_data.iterrows():
                name = row['Name']
                university = row['University']
                bio = generate_bio(name, university)
                data.at[index, 'Bio'] = bio

            # Display updated chunk
            updated_chunk = data.iloc[chunk_index * chunk_size:(chunk_index + 1) * chunk_size]
            st.write("### Updated Chunk with Bios:")
            st.write(updated_chunk)

            # Download updated chunk
            csv = updated_chunk.to_csv(index=False)
            st.download_button(
                label="Download Current Chunk as CSV",
                data=csv,
                file_name=f"chunk_{chunk_index}_bios.csv",
                mime="text/csv"
            )
    else:
        st.error(f"The uploaded file must contain the following columns: {required_columns}")
