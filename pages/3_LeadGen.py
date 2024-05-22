import os
import openai
import streamlit as st

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
       "A collection of Multi AI Agent Systems "
            )
    st.markdown(
       "This tool is a work in progress. "
            )
    openai_api_key = st.text_input("OpenAI API Key", key="file_qa_api_key", type="password")
    "[View the source code](https://github.com/natnew/Conference-Research/RAG.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("💬 Lead Generation")
st.markdown("Generate Professional Email Templates for Conference Preparation: Tailor Your Communication for Effective Networking and Engagement")


def gen_mail_contents(email_contents):
    for topic in range(len(email_contents)):
        input_text = email_contents[topic]
        rephrased_content = openai.Completion.create(
            engine="text-davinci-002",
            prompt=f"Rewrite the text to be elaborate and polite.\nAbbreviations need to be replaced.\nText: {input_text}\nRewritten text:",
            temperature=0.8,
            max_tokens=len(input_text)*3,
            top_p=0.8,
            best_of=2,
            frequency_penalty=0.0,
            presence_penalty=0.0)
        email_contents[topic] = rephrased_content.get("choices")[0]['text']
    return email_contents

def gen_mail_format(sender, recipient, style, email_contents):
    email_contents = gen_mail_contents(email_contents)
    contents_str, contents_length = "", 0
    for topic in range(len(email_contents)):
        contents_str = contents_str + f"\nContent{topic+1}: " + email_contents[topic]
        contents_length += len(email_contents[topic])
    email_final_text = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Write a professional email sounds {style} and includes Content1 and Content2 in that order.\n\nSender: {sender}\nRecipient: {recipient} {contents_str}\n\nEmail Text:",
        temperature=0.8,
        max_tokens=contents_length*2,
        top_p=0.8,
        best_of=2,
        frequency_penalty=0.0,
        presence_penalty=0.0)
    return email_final_text.get("choices")[0]['text']

def main_gpt3emailgen():
    try:
        st.image('../con_research/data/Email_Generator.jpg')  # Use relative path from the /pages directory
    except FileNotFoundError:
        st.warning("Image file not found. Continuing without displaying the image.")
    
    st.markdown('Generate professional sounding emails based on your direct comments - powered by Artificial Intelligence (OpenAI GPT-3) '
        
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
                if not openai_api_key:
                    st.info("Please add your OpenAI API key to continue.")
                else:
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
                            openai.api_key = openai_api_key
                            email_text = gen_mail_format(input_sender, input_recipient, input_style, input_contents)

    if email_text:
        st.write('\n')
        st.subheader('\nYou sound incredibly professional!\n')
        with st.expander("SECTION - Email Output", expanded=True):
            st.markdown(email_text)

if __name__ == '__main__':
    main_gpt3emailgen()
