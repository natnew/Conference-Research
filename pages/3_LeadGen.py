import streamlit as st
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Load the model and tokenizer
model_name = "Helsinki-NLP/opus-mt-en-ro"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

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

def generate_email(sender, recipient, style, topics):
    email_content = " ".join(topics)
    input_text = f"Generate a professional email in a {style} tone from {sender} to {recipient}. The email should cover the following topics: {email_content}"
    
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=512, num_beams=5, early_stopping=True)
    email = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return email

def main():
    st.markdown('Generate professional sounding emails based on your direct comments - powered by AI '
        'view project source code on '
        '[GitHub](https://github.com/natnew/Conference-Research)')
    st.write('\n')

    st.subheader('\nWhat is your email all about?\n')
    with st.expander("SECTION - Email Input", expanded=True):
        input_c1 = st.text_input('Enter email contents down below! (currently 2x separate topics supported)', 'topic 1')
        input_c2 = st.text_input('', 'topic 2 (optional)')

        email_text = ""
        col1, col2, col3, space, col4 = st.columns([5, 5, 5, 0.5, 5])
        with col1:
            input_sender = st.text_input('Sender Name', '[rephraise]')
        with col2:
            input_recipient = st.text_input('Recipient Name', '[recipient]')
        with col3:
            input_style = st.selectbox('Writing Style', ('formal', 'motivated', 'concerned', 'disappointed'), index=0)
        with col4:
            st.write("\n")
            st.write("\n")
            generate_button = st.button('Generate Email')

            if generate_button:
                input_contents = []
                if input_c1 and input_c1 != 'topic 1':
                    input_contents.append(str(input_c1))
                if input_c2 and input_c2 != 'topic 2 (optional)':
                    input_contents.append(str(input_c2))

                if not input_contents:
                    st.write('Please fill in some contents for your message!')
                elif not input_sender or not input_recipient:
                    st.write('Sender and Recipient names cannot be empty!')
                else:
                    with st.spinner():
                        email_text = generate_email(input_sender, input_recipient, input_style, input_contents)

    if email_text:
        st.write('\n')
        st.subheader('\nYou sound incredibly professional!\n')
        with st.expander("SECTION - Email Output", expanded=True):
            st.markdown(email_text)

if __name__ == '__main__':
    main()
