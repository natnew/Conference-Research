import openai
import streamlit as st
import pandas as pd

# Function to call GPT API to generate a bio
def generate_bio_with_gpt(api_key, model_name, full_name, interests, publications):
    openai.api_key = api_key
    
    # GPT Prompt
    prompt = f"""
    Generate a professional bio for the following academic profile:

    Name: {full_name}
    Research/Teaching Interests: {interests}
    Recent Publications: {publications}

    The bio should be concise and professional.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert academic bio generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        bio = response['choices'][0]['message']['content'].strip()
        return bio
    except Exception as e:
        return f"Error generating bio: {e}"

# Example search_internet function to demonstrate integration with GPT
def search_internet_with_gpt(api_key, model_name, full_name, university):
    # Mock data from scraping module
    research_interests = "class, gender, and liberation"
    publications = "Paper A on ScienceDirect, Paper B on SpringerLink"
    
    # Generate bio using GPT API
    bio = generate_bio_with_gpt(api_key, model_name, full_name, research_interests, publications)
    
    # Mock additional details
    email = "N/A"
    university_location = "Europe"
    
    return [{
        "Name": full_name,
        "Email": email,
        "University Location": university_location,
        "Bio": bio,
        "Published Papers": publications
    }]

# Streamlit App UI
def main():
    st.title("Bio Generator with GPT")
    st.markdown("Generate professional academic bios using GPT models.")
    
    # API Configuration
    st.markdown("### API Configuration")
    api_key = st.text_input("API Key", type="password", help="Enter your OpenAI API key.")
    model_name = st.selectbox("Choose a Model", ["gpt-4", "gpt-3.5-turbo"], help="Select the GPT model to use.")
    
    # User Inputs
    full_name = st.text_input("Full Name (First and Last Name)")
    university = st.text_input("University")
    
    # Generate Bio Button
    if st.button("Generate Bio"):
        if not api_key:
            st.error("Please provide an API key.")
        elif not full_name:
            st.error("Please provide a full name.")
        else:
            with st.spinner("Generating bio..."):
                results = search_internet_with_gpt(api_key, model_name, full_name, university)
                st.write("### Results")
                st.table(pd.DataFrame(results))

# Run the app
if __name__ == "__main__":
    main()
