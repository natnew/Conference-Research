import openai
import streamlit as st

# Function to call GPT API to generate a bio
def chat_with_gpt(api_key, model_name, prompt):
    """
    Function to send a prompt to OpenAI's GPT model and return the response.

    Args:
        api_key (str): The OpenAI API key.
        model_name (str): The GPT model to use (e.g., "gpt-4").
        prompt (str): The input prompt for the model.

    Returns:
        str: The response content from the GPT model.
    """
    openai.api_key = api_key
    try:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert academic bio generator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,  # Creativity in responses
            max_tokens=200,  # Limit the token count for concise bios
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        return f"Error: {e}"

# Function to generate a bio prompt
def generate_bio_prompt(full_name, university):
    """
    Constructs a professional bio prompt for GPT.

    Args:
        full_name (str): The individual's name.
        university (str): The university name.

    Returns:
        str: The formatted prompt for GPT.
    """
    return f"""
    Generate a professional academic bio for the following individual:

    Name: {full_name}
    University: {university}

    Please infer their research and teaching interests based on their academic background
    and their likely expertise. Include notable achievements, focus areas, and recent publications 
    if available. The bio should be concise, professional, and focused on the individual.
    """

# Streamlit App for BioGen
def main():
    # Page Title
    st.title("BioGen - Professional Bio Generator")
    st.markdown("Generate professional academic bios using GPT models based on Name and University.")

    # API Configuration
    st.markdown("### API Configuration")
    api_key = st.text_input("API Key", type="password", help="Enter your OpenAI API key.")
    model_name = st.selectbox("Choose a Model", ["gpt-4", "gpt-3.5-turbo"], help="Select the GPT model to use.")

    # User Inputs for Bio Generation
    st.markdown("### Academic Profile Details")
    full_name = st.text_input("Full Name (First and Last Name)", help="Enter the full name of the academic.")
    university = st.text_input("University", help="Enter the university of the individual.")

    # Generate Bio Button
    if st.button("Generate Bio"):
        # Validate Inputs
        if not api_key:
            st.error("Please provide an API key.")
        elif not full_name:
            st.error("Please provide the full name.")
        elif not university:
            st.error("Please provide the university.")
        else:
            with st.spinner("Generating bio..."):
                # Construct the GPT prompt
                prompt = generate_bio_prompt(full_name, university)
                
                # Call the GPT function to generate the bio
                bio = chat_with_gpt(api_key, model_name, prompt)
                
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
        This tool uses advanced AI technologies to generate academic bios based on 
        Name and University. By leveraging GPT models, it infers professional details, 
        research interests, and achievements to create a concise and accurate bio.
        """)

# Run the App
if __name__ == "__main__":
    main()
