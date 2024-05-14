from con_research.src.modules.imports import *
from con_research.src.modules.scrapping_module import ContentScraper
from con_research.src.modules.search_module import SerperDevTool
def generate_short_bio(groq_api_key,bio_content):
    """
    Generates a short, concise bio from the scraped content using an LLM.
    
    :param content: The scraped content from the internet
    :return: A short bio formatted from the scraped content
    """
    # llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0,api_key=openai_api_key)
    llm = ChatGroq(temperature=0, model_name="llama3-70b-8192",api_key=groq_api_key)
    prompt = PromptTemplate(
        template="""Generate a short bio of not more than 100 words from the following content:\n{content}""",
        input_variables=["content"]
    )
    llm_chain = prompt | llm
    short_bio = llm_chain.invoke(input={"content":bio_content},)
    return short_bio.content
def main():
    st.title("Bio Generator")

    # OpenAI API Key Input
    openai_api_key = st.secrets["openai_api_key"]
    # GROQ API Key Input
    groq_api_key = st.secrets["groq_api_key"]

    # Serper API Key Input
    serper_api_key = st.secrets["serper_api_key"]

    # File Upload Section
    st.subheader("Upload Excel File")
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

        # Display uploaded DataFrame
        st.write("Uploaded DataFrame:")
        st.write(df)

        # Processing and displaying bios
        if st.button("Generate Bios"):
            df_with_bios = process_bios(df, groq_api_key, serper_api_key)
            st.write("DataFrame with Bios:")
            st.write(df_with_bios)

            # Download Button
            st.markdown(get_table_download_link(df_with_bios), unsafe_allow_html=True)


def process_bios(df, groq_api_key, serper_api_key):
    df["Bio"] = ""
    batch_size = 10

    for start_idx in range(0, len(df), batch_size):
        end_idx = start_idx + batch_size
        batch_df = df.iloc[start_idx:end_idx]  # Get a batch of rows from DataFrame

        for index, row in batch_df.iterrows():
            name = row["Name"]
            university = row["University"]

            # Generate search query
            query = f"{name} {university}"

            # Search the internet using Serper with provided API key
            tool = SerperDevTool(api_key=serper_api_key)
            search_results = tool._run(query)

            # Scrape content from the obtained URLs
            bio_content = ""
            for url in search_results:
                # scraping_tool = SeleniumScraping(website_url=url)
                # content = scraping_tool._run()
                content = ContentScraper.scrape_anything(url)
                bio_content += content + "\n"

            # Pass the scraped content through LLM to format as a short, concise bio
            formatted_bio = generate_short_bio(groq_api_key, bio_content)

            # Update the Bio column
            df.at[index, "Bio"] = formatted_bio

        # Sleep for 30 seconds before processing the next batch
        time.sleep(30)

    return df


# Function to create a download link for a DataFrame
def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="bios.csv">Download Bios CSV</a>'
    return href


if __name__ == "__main__":
    main()
