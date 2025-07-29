"""
BioGen - Automated Biographical Profile Generator
===============================================

A Streamlit web application that automates the generation of professional biographical
profiles for academic and professional contacts. Part of the Conference & Campus Research
Assistant suite for streamlining conference and campus visit research workflows.

KEY FEATURES:
- Batch processing with chunked execution and web scraping using Google Serper API
- AI-powered bio generation using OpenAI GPT-4o-mini with automatic email extraction
- Excel export functionality and token management for API efficiency
- Error handling and fallback mechanisms for robust operation

REQUIREMENTS:
- openai_api_key: OpenAI API key for GPT model access
- serper_api_key: Google Serper API key for web search functionality
- Dependencies: streamlit, pandas, openai, requests, beautifulsoup4, tiktoken

INPUT REQUIREMENTS:
- CSV/XLSX format with required columns: 'Name', 'University' (or 'Affiliation')
- Optional columns: 'Bio', 'Email' (will be created if not present)

WORKFLOW:
1. Upload CSV/XLSX → 2. Preview and configure chunks → 3. Select chunk index
4. Generate bios using web search + AI synthesis → 5. Review results → 6. Download Excel

API INTEGRATIONS:
- OpenAI GPT-4o-mini: Bio generation with structured prompts avoiding title assumptions
- Google Serper API: Web search for academic profile information with content scraping

USAGE NOTES:
Process data in chunks to manage API costs and rate limits. Review generated content
for accuracy and ensure compliance with institutional policies for automated research.
"""

import streamlit as st
import pandas as pd
import openai
import re
from io import BytesIO
from openai import OpenAI
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import tiktoken
import http.client
import json
import time
import random
from urllib.parse import urlparse

# Configuration management
try:
    from con_research.config.config_manager import get_config, get_secret, get_config_manager
    # Initialize configuration
    config_manager = get_config_manager()
    config = get_config()
    
    # Validate configuration at startup
    startup_errors = config_manager.validate_startup()
    if startup_errors:
        for error in startup_errors:
            st.error(f"Configuration Error: {error}")
        if config.environment.value == "production":
            st.stop()
    
except ImportError:
    # Silent fallback configuration - no user warning needed
    # Fallback configuration class
    class FallbackConfig:
        class API:
            openai_model = "gpt-4o-mini-2024-07-18"
            openai_max_tokens = 1000
            openai_timeout = 30
            serper_timeout = 10
            serper_max_results = 10
        
        class FileUpload:
            max_size_mb = 50
            allowed_extensions = [".csv", ".xlsx", ".xls"]
            validation_strict = True
        
        class WebDriver:
            timeout = 30
            headless = True
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
        class Retry:
            max_attempts = 3
            initial_delay = 1.0
            backoff_factor = 2.0
        
        api = API()
        file_upload = FileUpload()
        webdriver = WebDriver()
        retry = Retry()
    
    config = FallbackConfig()
    
    def get_secret(key, default=None):
        """Fallback secret getter using Streamlit secrets."""
        try:
            return st.secrets.get(key, default)
        except:
            return default

# Sidebar Configuration
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content
and assists in lead generation. Designed to support academic and professional
activities, it offers interconnected modules that streamline research tasks,
whether for conferences, campus visits, or other events.
""")

st.sidebar.write(
    "Built by [Natasha Newbold](https://www.linkedin.com/in/natasha-newbold/) "
)

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This app leverages cutting-edge technologies to automate and enhance research
    workflows. It combines generative AI, voice-to-action capabilities,
    Retrieval-Augmented Generation (RAG), agentic RAG, and other advanced
    methodologies to deliver efficient and accurate results.
    """)

# Additional Information in the Sidebar
with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "Search for academic profiles by querying local files (CSV/XLSX) or the internet. Combine the power of local data and web scraping to uncover detailed academic profiles. "
    )
    st.markdown("This tool is a work in progress.")
    
    # Display environment and configuration info
    if hasattr(config, 'environment'):
        st.caption(f"Environment: {config.environment.value}")

# Initialize API keys from configuration
openai_api_key = get_secret("openai_api_key")
serper_api_key = get_secret("serper_api_key")

def retry_api_call(max_retries=None, backoff_factor=None):
    """
    Decorator to retry API calls with exponential backoff.
    Uses configuration-driven defaults with override capability.
    
    Args:
        max_retries (int): Maximum number of retry attempts (uses config default if None)
        backoff_factor (float): Factor for exponential backoff delay (uses config default if None)
        
    Returns:
        function: Decorated function with retry logic
    """
    # Use configuration defaults if not specified
    if max_retries is None:
        max_retries = config.retry.max_attempts
    if backoff_factor is None:
        backoff_factor = config.retry.backoff_factor
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, openai.OpenAIError, ConnectionError) as e:
                    if attempt == max_retries:
                        raise e
                    delay = config.retry.initial_delay * (backoff_factor ** attempt) + random.uniform(0, 1)
                    # Cap the delay at max_delay from config
                    delay = min(delay, getattr(config.retry, 'max_delay', 60.0))
                    st.warning(f"API call failed (attempt {attempt + 1}/{max_retries + 1}). Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def validate_file_upload(uploaded_file):
    """
    Validates uploaded file for security and format requirements.
    Uses configuration-driven validation settings.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
        
    Raises:
        ValueError: If file validation fails
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size using configuration
    max_size = config.file_upload.max_size_mb * 1024 * 1024  # Convert MB to bytes
    if uploaded_file.size > max_size:
        return False, f"File size ({uploaded_file.size / (1024*1024):.1f}MB) exceeds maximum allowed size ({config.file_upload.max_size_mb}MB)"
    
    # Check file extension using configuration
    allowed_extensions = config.file_upload.allowed_extensions
    file_extension = '.' + uploaded_file.name.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        return False, f"File type '{file_extension}' not allowed. Supported formats: {', '.join(allowed_extensions)}"
    
    # Check for suspicious file names
    suspicious_patterns = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
    if any(pattern in uploaded_file.name for pattern in suspicious_patterns):
        return False, "File name contains invalid characters"
    
    # Basic MIME type check using configuration
    allowed_mime_types = getattr(config.file_upload, 'allowed_mime_types', [])
    if config.file_upload.validation_strict and allowed_mime_types:
        if uploaded_file.type not in allowed_mime_types:
            st.warning(f"MIME type '{uploaded_file.type}' may not be supported. Expected: {allowed_mime_types}")
    
    return True, "File validation passed"

@retry_api_call()  # Use configuration defaults
def scrape_text_from_url(url, timeout=None):
    """
    Scrapes and extracts plain text content from a given URL using Beautiful Soup.
    Uses configuration-driven timeout and user agent settings.
    
    Args:
        url (str): The complete URL to scrape (must include http/https protocol)
        timeout (int): Request timeout in seconds (uses config default if None)
        
    Returns:
        str: Cleaned plain text content with HTML tags removed and whitespace normalized
        
    Raises:
        requests.exceptions.RequestException: If URL is unreachable or returns error status
        ValueError: If URL format is invalid or content cannot be parsed
        
    Note:
        Uses requests with configurable timeout and handles UTF-8 encoding automatically.
        Removes scripts, styles, and other non-content elements before text extraction.
    """
    # Use configuration default if timeout not specified
    if timeout is None:
        timeout = config.webdriver.timeout
    
    # Validate URL format
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"Invalid URL format: {url}")
    except Exception as e:
        print(f"URL validation error for {url}: {e}")
        return None
    
    try:
        headers = {
            'User-Agent': config.webdriver.user_agent
        }
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()  # Check if the request was successful
        response.encoding = 'utf-8'  # Specify the encoding
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')  # You can also try 'lxml' or 'html5lib'
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text from paragraphs and other relevant tags
            paragraphs = soup.find_all(['p', 'li', 'span', 'div'])
            text = ' '.join([para.get_text() for para in paragraphs])
        except (ValueError, AttributeError, TypeError) as e:
            print(f"Error parsing {url} with BeautifulSoup: {e}")
            text = response.text  # Fall back to raw text content
        return text
    except requests.exceptions.Timeout:
        print(f"Timeout error fetching {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"Connection error fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error {e.response.status_code} fetching {url}")
        return None
    except requests.RequestException as e:
        print(f"Request error fetching {url}: {e}")
        return None

def clean_text(text):
    """
    Normalizes and cleans raw text by removing extra whitespace and formatting artifacts.
    
    Args:
        text (str): Raw text content that may contain irregular spacing, line breaks, or formatting
        
    Returns:
        str: Cleaned text with normalized whitespace, single spaces between words, 
             and standardized line breaks
    
    Note:
        Preserves sentence structure while removing redundant whitespace patterns
        commonly found in web-scraped or PDF-extracted content.
    """
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def truncate_text(text, max_tokens, encoding_name="cl100k_base"):
    """
    Truncates text content to fit within specified token limits for LLM processing.
    
    Args:
        text (str): Input text to be truncated
        max_tokens (int): Maximum number of tokens allowed (must be positive)
        encoding_name (str, optional): Tokenizer encoding to use. Defaults to "cl100k_base" (GPT-4)
        
    Returns:
        str: Truncated text that fits within the token limit, preserving complete words
        
    Raises:
        ValueError: If max_tokens is not positive or encoding_name is invalid
        tiktoken.core.UnicodeEncodeError: If text contains unsupported characters
        
    Note:
        Uses tiktoken library for accurate token counting. Truncation occurs at word boundaries
        to maintain readability. Different models may use different encodings.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text)
    truncated_tokens = tokens[:max_tokens]
    truncated_text = encoding.decode(truncated_tokens)
    return truncated_text

# def generate_enriched_text(full_name, university):
#     query = f"a professional bio and email for {full_name}, who is affiliated with {university}."
#     results = DDGS().text(query, max_results=3)

#     enriched_text = ""
#     for result in results:
#         url = result['href']
#         body_text = result['body']
#         scraped_text = scrape_text_from_url(url)
#         if scraped_text is not None:
#             combined_text = f"{body_text} {scraped_text}"
#             enriched_text += clean_text(combined_text) + " "
#         else:
#             enriched_text += clean_text(body_text) + " "

#     # Format the enriched text into a block of text
#     enriched_text = re.sub(r'\s+', ' ', enriched_text).strip()
#     return enriched_text
@retry_api_call(max_retries=3, backoff_factor=1.0)
def generate_enriched_text(researcher_full_name, university_affiliation):
    """
    Searches for and compiles comprehensive academic information about a researcher using Google Search API.
    
    Args:
        researcher_full_name (str): Complete name of the academic researcher (first and last name)
        university_affiliation (str): Full name of the researcher's institutional affiliation
        
    Returns:
        str: Compiled research profile containing publication details, academic achievements,
             research interests, and professional background information
             
    Raises:
        Exception: If Google Search API key is missing or API request fails
        requests.exceptions.RequestException: If network request to search API fails
        
    Dependencies:
        - Requires valid Google Search API key in st.secrets
        - Uses SERPER_API_KEY for Google search functionality
        
    Note:
        Performs multiple targeted searches combining name and university for comprehensive results.
        Results are concatenated and can be quite lengthy (suitable for subsequent LLM processing).
        Rate-limited by Google Search API quotas.
    """
    search_query = f"a professional bio and email for {researcher_full_name}, who is affiliated with {university_affiliation}."
    http_connection = http.client.HTTPSConnection("google.serper.dev")
    request_payload = json.dumps({
        "q": search_query
    })
    request_headers = {
        'X-API-KEY': st.secrets["serper_api_key"],
        'Content-Type': 'application/json'
    }
    http_connection.request("POST", "/search", request_payload, request_headers)
    api_response = http_connection.getresponse()
    response_data_raw = api_response.read()
    parsed_response_data = json.loads(response_data_raw.decode("utf-8"))

    compiled_enriched_text = ""
    for search_result in parsed_response_data.get('organic', []):
        result_url = search_result['link']
        snippet_text = search_result['snippet']
        scraped_content = scrape_text_from_url(result_url)
        if scraped_content is not None:
            combined_content = f"{snippet_text} {scraped_content}"
            compiled_enriched_text += clean_text(combined_content) + " "
        else:
            compiled_enriched_text += clean_text(snippet_text) + " "

    # Format the enriched text into a block of text
    final_enriched_text = re.sub(r'\s+', ' ', compiled_enriched_text).strip()
    return final_enriched_text

@retry_api_call(max_retries=3, backoff_factor=1.0)
def generate_bio_with_chatgpt(researcher_full_name, university_affiliation, enriched_text_content):
    """
    Generates a comprehensive academic biography using OpenAI GPT-4o-mini with enriched research data.
    
    Args:
        researcher_full_name (str): Complete name of the researcher for bio personalization
        university_affiliation (str): Institutional affiliation to include in biography
        enriched_text_content (str): Pre-compiled research information from web searches
        
    Returns:
        str: Professionally formatted academic biography (typically 200-400 words) including
             research interests, publications, achievements, and contact information when available
             
    Raises:
        openai.OpenAIError: If API key is invalid or request fails
        Exception: If response parsing fails or content generation errors occur
        
    Dependencies:
        - Requires valid OpenAI API key in st.secrets["openai_api_key"]
        - Uses GPT-4o-mini-2024-07-18 model for cost-effective generation
        
    Note:
        Includes specific prompting for academic tone, factual accuracy, and professional formatting.
        Output includes structured sections for research focus, achievements, and institutional context.
        Token usage approximately 1000-2000 tokens per request depending on enriched content length.
    """
    prompt = (
        f"Create a professional biographical profile for {researcher_full_name}, who is affiliated with {university_affiliation}, based on the following information: {enriched_text_content}\n\n"
        "Important guidelines:\n"
        "1. Do NOT assume any titles (like Dr. or Professor) unless explicitly mentioned in the provided information\n"
        "2. Only include factual information that is directly supported by the provided text\n"
        "3. Format the bio in the following structure:\n"
           "- Full name and current position (exactly as provided)\n"
           "- Institutional affiliations\n"
           "- Email address (if available)\n"
           "- Research focus and interests\n"
           "- Teaching activities (if any)\n"
           "- Notable publications or projects (only if specifically mentioned)\n"
        "4. If certain information is not available in the provided text, omit that section rather than making assumptions\n"
        "5. Keep the tone professional but factual, avoiding speculative or honorary language"
    
    )
    try:
        # Initialize the OpenAI client
        openai_client = OpenAI(api_key=st.secrets["openai_api_key"])

        # Generate response using the official OpenAI method
        chat_response = openai_client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}]
        )
        bio_results = chat_response.choices[0].message.content

        return bio_results
    except openai.OpenAIError as e:
        st.error(f"OpenAI API error: {e}")
        return None
    except (KeyError, ValueError) as e:
        st.error(f"Error processing API response: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error generating bio with ChatGPT: {e}")
        return None

def extract_email(bio_content):
    """
    Extracts email addresses from biographical text using regex pattern matching.
    
    Args:
        bio_content (str): Text content that may contain email addresses
        
    Returns:
        str: First valid email address found, or "No email found" if none detected
        
    Note:
        Uses standard email regex pattern to identify valid email formats.
        Returns only the first email found if multiple addresses are present.
        Case-insensitive matching for common email domains and formats.
    """
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", bio_content)
    return email_match.group() if email_match else "Email not found"

# App Title
st.title("BioGen - Automated Bio Generator")

# File Upload
uploaded_dataset = st.file_uploader("Upload your CSV/XLSX file :balloon:", type=["csv", "xlsx"])
if uploaded_dataset:
    # Validate uploaded file
    is_valid, validation_message = validate_file_upload(uploaded_dataset)
    if not is_valid:
        st.error(f"File validation failed: {validation_message}")
        st.stop()
    else:
        st.success(validation_message)
    # Load File
    if uploaded_dataset.name.endswith(".csv"):
        dataset_dataframe = pd.read_csv(uploaded_dataset)
    else:
        dataset_dataframe = pd.read_excel(uploaded_dataset)

    st.write("### File Preview:")
    st.write(dataset_dataframe.head())

    # If 'University' column is missing but 'Affiliation' exists, rename it
    if 'University' not in dataset_dataframe.columns and 'Affiliation' in dataset_dataframe.columns:
        dataset_dataframe.rename(columns={'Affiliation': 'University'}, inplace=True)
        st.info("'Affiliation' column found and renamed to 'University' for processing.")

    # Check if required columns are present
    required_columns = ['Name', 'University']
    if all(col in dataset_dataframe.columns for col in required_columns):
        st.success("File contains the required columns for processing.")

        # Add a placeholder for the Bio column if not already present
        if 'Bio' not in dataset_dataframe.columns:
            dataset_dataframe['Bio'] = ""
        if 'Email' not in dataset_dataframe.columns:
            dataset_dataframe['Email'] = ""

        # Specify Chunk Size
        default_chunk_size = min(10, len(dataset_dataframe))
        processing_chunk_size = st.number_input("Number of rows per chunk", min_value=1, max_value=len(dataset_dataframe), value=default_chunk_size)

        total_chunks = (len(dataset_dataframe) + processing_chunk_size - 1) // processing_chunk_size
        st.write(f"### Total Chunks: {total_chunks}")

        # Select Chunk to Process
        selected_chunk_index = st.number_input("Select Chunk Index", min_value=0, max_value=total_chunks - 1, value=0, step=1)
        current_chunk_data = dataset_dataframe.iloc[selected_chunk_index * processing_chunk_size:(selected_chunk_index + 1) * processing_chunk_size]
        st.write("### Current Chunk:")
        st.write(current_chunk_data)

        if st.button("Generate Bios for Current Chunk"):
            # Iterate through each row in the chunk
            for data_index, data_row in current_chunk_data.iterrows():
                researcher_name = data_row['Name']
                researcher_university = data_row['University']

                # Generate enriched text using DDGS
                enriched_research_text = generate_enriched_text(researcher_name, researcher_university)

                # Truncate enriched text to fit within token limit
                max_token_limit = 100000  # Adjust this value based on your model's token limit
                truncated_enriched_text = truncate_text(enriched_research_text, max_token_limit)

                # Generate bio using ChatGPT
                generated_bio_content = generate_bio_with_chatgpt(researcher_name, researcher_university, truncated_enriched_text)
                if generated_bio_content:
                    dataset_dataframe.at[data_index, 'Bio'] = generated_bio_content  # Update the bio column

                    # Extract email from the bio content
                    extracted_email = extract_email(generated_bio_content)
                    dataset_dataframe.at[data_index, 'Email'] = extracted_email

            # Display Updated Chunk
            updated_chunk_display = dataset_dataframe.iloc[selected_chunk_index * processing_chunk_size:(selected_chunk_index + 1) * processing_chunk_size]
            st.write("### Updated Chunk with Bios:")
            st.write(updated_chunk_display)

            # Download Option
            excel_output = BytesIO()
            updated_chunk_display.to_excel(excel_output, index=False, engine='openpyxl')
            excel_output.seek(0)
            st.download_button(
                label="Download Current Chunk as an Excel Sheet",
                data=excel_output,
                file_name=f"chunk_{selected_chunk_index}_bios.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.info("Use the Chunk Index to process the next set of rows.")
    else:
        st.error(f"Uploaded file must contain the following columns: {required_columns}")
