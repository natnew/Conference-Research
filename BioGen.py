import openai
import streamlit as st

# Function to call GPT API to generate a bio
def chat_with_gpt(prompt, api_key, model="gpt-4"):
    """
    Function to send a prompt to OpenAI's GPT model and return the response.

    Args:
        prompt (str): The input prompt for the model.
        model (str): The GPT model to use (default is "gpt-4").
    
    Returns:
        str: The response content from the GPT model.
    """
    openai.api_key = api_key
    try:
        # Send the request to the OpenAI API
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        # Extract and return the model's response
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Handle exceptions and print the error
        return f"An error occurred: {str(e)}"

# Function to generate a bio prompt
def generate_bio_prompt(full_name, interests, publications):
    """
    Constructs a professional bio prompt for GPT.

    Args:
        full_name (str): The individual's name.
        interests (str): The research/teaching interests.
        publications (str): A list or description of recent publications.

    Returns:
        str: The formatted prompt for GPT.
    """
    return f"""
    Generate a professional bio for the following academic profile:

    Name: {full_name}
    Research/Teaching Interests: {interests}
    Recent Publications: {publications}

    The bio should be concise, professional, and focused on the individual.
    """

# Streamlit App for BioGen
def main():
    # Page Title
    st.title("BioGen - Professional Bio Generator")
    st.markdown("Generate professional academic bios using GPT models.")

    # API Configuration
    st.markdown("### API Configuration")
    api_key = st.text_input("API Key", type="password", help="Enter your OpenAI API key.")
    model_name = st.selectbox("Choose a Model", ["gpt-4", "gpt-3.5-turbo"], help="Select the GPT model to use.")

    # User Inputs for Bio Generation
    st.markdown("### Academic Profile Details")
    full_name = st.text_input("Full Name (First and Last Name)", help="Enter the full name of the academic.")
    interests = st.text_area("Research/Teaching Interests", help="Enter the individual's research or teaching interests.")
    publications = st.text_area(
        "Recent Publications", 
        help="Enter the titles of recent publications and, if possible, their sources (e.g., ScienceDirect, SpringerLink)."
    )

    # Generate Bio Button
    if st.button("Generate Bio"):
        # Validate Inputs
        if not api_key:
            st.error("Please provide an API key.")
        elif not full_name:
            st.error("Please provide the full name.")
        elif not interests:
            st.error("Please provide the research/teaching interests.")
        elif not publications:
            st.error("Please provide recent publications.")
        else:
            with st.spinner("Generating bio..."):
                # Construct the GPT prompt
                prompt = generate_bio_prompt(full_name, interests, publications)
                
                # Call the GPT function to generate the bio
                bio = chat_with_gpt(prompt, api_key, model_name)
                
                # Display the result
                if "Error" in bio:
                    st.error(bio)
                else:
                    st.success("Bio Generated Successfully!")
                    st.markdown("### Generated Bio")
                    st.write(bio)

    # About Section in Sidebar
    with st.sidebar.expander("Capabilities", expanded=False):
        st.write("""
        This tool leverages cutting-edge AI technologies to generate professional 
        academic bios. By combining user-provided data with the power of GPT models, 
        BioGen delivers accurate and concise biographical content tailored to 
        researchers, academics, and professionals.
        """)

# Run the App
if __name__ == "__main__":
    main()
