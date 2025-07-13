import streamlit as st
import pandas as pd
import re
from openai import OpenAI


# Sidebar Configuration
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content 
and assists in lead generation. Designed to support academic and professional 
activities, it offers interconnected modules that streamline research tasks, 
whether for conferences, campus visits, or other events.
""")

# Additional Sidebar Info
with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "Search for academic profiles by querying local files (CSV/XLSX) or the internet. Combine the power of local data and AI-generated bios to uncover detailed academic profiles."
    )
    st.markdown("This tool is a work in progress.")
    st.page_link("pages/1_About.py", label="About", icon="ℹ️")
    openai_api_key = st.secrets["openai_api_key"]

# Bio Generation Function
def generate_bio_with_chatgpt(full_name, university):
    """
    Generate a professional bio using OpenAI's ChatGPT API.
    """
    prompt = (
        f"Generate a professional bio for {full_name}, who is affiliated with {university}. "
        "Include their research interests, teaching interests, any paper titles they may have published, "
        "and contact information such as email."
    )
    try:
        # Initialize the OpenAI client
        client = OpenAI(api_key=openai_api_key)

        # Generate response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating bio: {e}"

# Main Function
def main():
    st.title("Desktop Research")
    st.markdown("Search for academic profiles by querying local files (CSV/XLSX) or the internet. :balloon:")

    # User Input Fields
    full_name = st.text_input("Full Name (First and Last Name)")
    university = st.text_input("University")
    search_scope = st.selectbox("Where would you like to search?", ["Local Files", "Internet", "Both"])

    # Optional File Upload
    uploaded_files = st.file_uploader("Upload CSV/XLSX files (optional for local search)", type=["csv", "xlsx"], accept_multiple_files=True)

    if st.button("Search"):
        if search_scope == "Internet":
            # Internet Search with ChatGPT
            if full_name and university:
                st.write("### Generating Bio with AI...")
                bio_content = generate_bio_with_chatgpt(full_name, university)
                st.write("### Bio Content:")
                st.write(bio_content)

                # Extract Email
                email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", bio_content)
                email_address = email_match.group() if email_match else "Email not found"
                st.write(f"### Extracted Email: {email_address}")
            else:
                st.error("Please provide both Full Name and University.")

        if search_scope in ["Local Files", "Both"]:
            # Process Local File Search
            if uploaded_files:
                st.write("### Searching in Local Files...")
                for file in uploaded_files:
                    if file.name.endswith(".csv"):
                        df = pd.read_csv(file)
                    else:
                        df = pd.read_excel(file)

                    st.write("### File Preview:")
                    st.write(df.head())

                    # Check required columns
                    if 'Name' in df.columns and 'University' in df.columns:
                        st.success("File contains required columns.")
                        df['Bio'] = df.apply(
                            lambda row: generate_bio_with_chatgpt(row['Name'], row['University']), axis=1
                        )
                        st.write("### Updated Data:")
                        st.write(df)

                        # Download Option
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Download Updated File",
                            data=csv,
                            file_name="updated_data_with_bios.csv",
                            mime="text/csv"
                        )
                    else:
                        st.error("Uploaded file must contain 'Name' and 'University' columns.")
            else:
                st.warning("Please upload a file to search in local data.")

# Run the App
if __name__ == "__main__":
    main()
