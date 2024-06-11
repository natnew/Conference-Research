from con_research.src.modules.imports import *
from con_research.src.modules.scrapping_module import ContentScraper
from con_research.src.modules.search_module import SerperDevTool

###
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Load configuration file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Substitute environment variables in the config
for username in config['credentials']['usernames']:
    config['credentials']['usernames'][username]['password'] = st.secrets[username.upper() + '_PASSWORD']
config['cookie']['key'] = st.secrets['COOKIE_KEY']

# Create an authenticator object
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Add the login widget
name, authentication_status, username = authenticator.login(
    'main', 'Login', fields=('username', 'password')
)

# Handle authentication status
if authentication_status:
    st.success(f'Welcome {name}')
    # Your main app code goes here
    st.title("Conference Research App")
    st.write("Add your main app logic here.")
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')


###


    st.markdown("""
        <style>
            .sidebar .sidebar-content {
                background-color: #f0f2f6;
                padding: 10px;
            }
            .main .block-container {
                padding: 10px;
            }
            h1 {
                color: #3c8dbc;
            }
            .stButton>button {
                background-color: #4CAF50;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("# About")
        st.markdown(
           "We use multi-agent systems and other AI technologies to power this app."
                )
        st.markdown("""
        This app helps conference attendees prepare for networking at a conference by automating the desktop research and lead generation email creation process.
        
            """)
    
        st.markdown(
           "This tool is a work in progress. "
                )
        "[View the source code](https://github.com/natnew/Conference-Research/RAG.py)"
        "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
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
    def generate_short_bio(bio_content, openai_api_key,max_tokens=128000):
        """
        Generates a short, concise bio from the scraped content using an LLM.
    
        :param bio_content: The scraped content from the internet
        :param openai_api_key: The API key for OpenAI
        :return: A short bio formatted from the scraped content
        """
        # Truncate bio_content to ensure it does not exceed the max_tokens
        truncated_content = truncate_content(bio_content, max_length=max_tokens)
        
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
        prompt = PromptTemplate(
            # template="Generate a short bio of not more than 100 words from the following content:\n{content}",
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
        short_bio = llm_chain.invoke(input={"content": truncated_content })
        return short_bio.content
    
    def process_bios(df, serper_api_key, openai_api_key):
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
                    content = ContentScraper.scrape_anything(url)
                    bio_content += content + "\n"
    
                # Pass the scraped content through LLM to format as a short, concise bio
                bio_content = truncate_content(bio_content, max_length=20000)
                
                formatted_bio = generate_short_bio(bio_content, openai_api_key)
    
                # Update the Bio column
                df.at[index, "Bio"] = formatted_bio
    
            # Sleep for 10 seconds before processing the next batch
            # time.sleep(10)
    
        return df
    
    def get_table_download_link(df,original_filename):
        base_filename = os.path.splitext(original_filename)[0]
        new_filename = f"{base_filename}_bios.xlsx"
        # Use a BytesIO buffer to save the Excel file to memory
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        # Get the buffer content as bytes
        buffer.seek(0)
        excel_bytes = buffer.getvalue()
    
        # Encode the bytes in base64
        b64 = base64.b64encode(excel_bytes).decode()
    
        # Create a download link
        # Create a download link
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{new_filename}">Download Bios Data</a>'
        return href
    
    def main():
        st.title("Bio Generator")
        st.markdown("Generate Detailed Bios for Conference Participants: Create Personalized Profiles for Effective Networking and Contact")
    
        # OpenAI API Key Input
        openai_api_key = st.secrets["openai_api_key"]
        # Serper API Key Input
        serper_api_key = st.secrets["serper_api_key"]
    
        # File Upload Section
        st.subheader("Upload Excel File")
        uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
    
        if uploaded_file is not None:
            # df = pd.read_excel(uploaded_file)
            df = pd.read_excel(uploaded_file, engine='openpyxl')
    
            # Display uploaded DataFrame
            st.write("Uploaded DataFrame:")
            st.write(df)
    
            # Processing and displaying bios
            if st.button("Generate Bios"):
                df_with_bios = process_bios(df, serper_api_key, openai_api_key)
                st.write("DataFrame with Bios:")
                st.write(df_with_bios)
                # Get the original filename
                original_filename = uploaded_file.name
    
                # Download Button
                st.markdown(get_table_download_link(df_with_bios, original_filename), unsafe_allow_html=True)
    
    if __name__ == "__main__":
        main()

###
elif authentication_status is False:
    st.error('Username/password is incorrect')
elif authentication_status is None:
    st.warning('Please enter your username and password')
