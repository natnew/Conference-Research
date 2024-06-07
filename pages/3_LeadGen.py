import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load the model and tokenizer
model_name = "distilgpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# DESIGN implement changes to the standard streamlit UI/UX
st.set_page_config(page_title="rephraise", page_icon="img/rephraise_logo.png")
# Design move app further up and remove top padding
st.markdown('''<style>.css-1egvi7u {margin-top: -4rem;}</style>''', unsafe_allow_html=True)
# Design change hyperlink href link color
st.markdown('''<style>.css-znku1x a {color: #9d03fc;}</style>''', unsafe_allow_html=True)  # darkmode
st.markdown('''<style>.css-znku1x a {color: #9d03fc;}</style>''', unsafe_allow_html=True)  # lightmode
# Design change height of text input fields headers
st.markdown('''<style>.css-qrbaxs {min-height: 0.0rem;}</style>''', unsafe_allow_html=True)
# Design change spinner color to primary color
st.markdown('''<style>.stSpinner > div > div {border-top-color: #9d03fc;}</style>''', unsafe_allow_html=True)
# Design change min height of text input box
st.markdown('''<style>.css-15tx938{min-height: 0.0rem;}</style>''', unsafe_allow_html=True)
# Design hide top header line
hide_decoration_bar_style = '''<style>header {visibility: hidden;}</style>'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)
# Design hide "made with streamlit" footer menu area
hide_streamlit_footer = """<style>#MainMenu {visibility: hidden;}
                        footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_footer, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# About")
    st.markdown(
       "We use multi-agent systems and other AI technologies to power this app. "
    )
    st.markdown(
       "This tool is a work in progress. "
    )

st.title("💬 Lead Generation")
st.markdown("Generate Professional Email Templates for Conference Preparation: Tailor Your Communication for Effective Networking and Engagement")

def generate_email_template(sender, recipient, style, subject):
    input_text = f"Generate a professional email in a {style} tone from {sender} to {recipient} about {subject}."
    
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
    email = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return email

def generate_email_from_prompt(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
    email = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return email

def main():
    st.markdown('Generate professional sounding emails based on your direct comments - powered by AI '
        'view project source code on '
        '[GitHub](https://github.com/natnew/Conference-Research)')
    st.write('\n')

    st.subheader('Choose Email Generation Method:')
    option = st.radio('Select an option:', ('Template Based', 'Prompt Based'))

    if option == 'Template Based':
        st.subheader('Email Template Input:')
        sender = st.text_input('Sender Name', '')
        recipient = st.text_input('Recipient Name', '')
        subject = st.text_input('Subject', '')
        style = st.selectbox('Writing Style', ('formal', 'motivated', 'concerned', 'disappointed'), index=0)

        generate_button = st.button('Generate Email Template')
        if generate_button:
            if sender and recipient and subject:
                with st.spinner('Generating email...'):
                    email_text = generate_email_template(sender, recipient, style, subject)
                    st.subheader('Generated Email:')
                    st.write(email_text)
            else:
                st.warning('Please fill out all fields.')

    elif option == 'Prompt Based':
        st.subheader('Email Prompt Input:')
        prompt = st.text_area('Enter a prompt for the email:', '')

        generate_button = st.button('Generate Email from Prompt')
        if generate_button:
            if prompt:
                with st.spinner('Generating email...'):
                    email_text = generate_email_from_prompt(prompt)
                    st.subheader('Generated Email:')
                    st.write(email_text)
            else:
                st.warning('Please enter a prompt.')

if __name__ == '__main__':
    main()
