import streamlit as st
import yaml
import pandas as pd
from yaml.loader import SafeLoader
from con_research.src.modules.scrapping_module import ContentScraper
from con_research.src.modules.search_module import SerperDevTool

# Remove authentication-related code, focus on API key usage

# Define your helper functions for processing bios
def truncate_content(content, max_length=20000):
    """
    Truncate content to ensure it does not exceed the specified maximum length.
    
    :param content: The content to be truncated
    :param max_length: The maximum length of the content
    :return: Truncated content
    """
    if len(content) > max_length:
        return content[:max_length]
    return content

def generate_short_bio(bio_content, openai_api_key, max_tokens=128000):
    """
    Generates a short, concise bio from the scraped content using an LLM.

    :param bio_content: The scraped content from the internet
    :param openai_api_key: The API key for OpenAI
    :return: A short bio formatted from the scraped content
    """
    truncated_content = truncate_content(bio_content, max_length=max_tokens)
    
    # Call OpenAI's API to generate a short bio
    llm = ChatOpenAI(model="gpt-4", temperature=0, api_key=openai_api_key)
    prompt = PromptTemplate(
        template="""
        Given the following content, generate a short bio of not more than 100 words. 
        If the content does not contain relevant information to generate a bio, respond with: 
        'I could not find information on this person.'

        Content:
        {content}
        """,
        input_variables=["content"]
    )
    llm_chain = prompt | llm
    short_bio = llm_chain.invoke(input={"content": truncated_content})
    return short_bio.content

def process_bios(df, serper_api_key, openai_api_key):
    df["Bio"] = ""
    batch_size = 10

    for start_idx in range(0, len(df), batch_size):
        end_idx = start_idx + batch_size
        batch_df = df.iloc[start_idx:end_idx]  # Get a batch of rows from DataFrame

        for index, row in batch_df.iterrows():
            name = row["Names"]
            university = row["University"]

            # Generate search query
            query = f"{name} {university}"

            # Search the internet using Serper with provided API key
            tool = SerperDevTool(api_key=serper_api_key)
            search_results = tool._run(query)

            # Scrape content from the obtained URLs
            bio_content = ""
            for url in search_results:
                content = ContentScraper.scrape_anything(url)
                bio_content += content + "\n"

            # Pass the scraped content through LLM to format as a short, concise bio
            bio_content = truncate_content(bio_content, max_length=20000)
            formatted_bio = generate_short_bio(bio_content, openai_api_key)

            # Update the Bio column
            df.at[index, "Bio"] = formatted_bio

    return df

def get_table_download_link(df, original_filename):
    base_filename = os.path.splitext(original_filename)[0]
    new_filename = f"{base_filename}_bios.xlsx"
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')

    buffer.seek(0)
    excel_bytes = buffer.getvalue()

    b64 = base64.b64encode(excel_bytes).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{new_filename}">Download Bios Data</a>'
    return href

# Main function
def main():
    st.title("Bio Generator")
    st.markdown("Generate Detailed Bios for Conference Participants: Create Personalized Profiles for Effective Networking and Contact")

    # API Key Inputs
    openai_api_key = st.secrets["openai_api_key"]
    serper_api_key = st.secrets["serper_api_key"]

    # File Upload Section
    st.subheader("Upload Excel File")
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, engine='openpyxl')

        # Display uploaded DataFrame
        st.write("Uploaded DataFrame:")
        st.write(df)

        # Processing and displaying bios
        if st.button("Generate Bios"):
            df_with_bios = process_bios(df, serper_api_key, openai_api_key)
            st.write("DataFrame with Bios:")
            st.write(df_with_bios)

            # Download Button
            original_filename = uploaded_file.name
            st.markdown(get_table_download_link(df_with_bios, original_filename), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
