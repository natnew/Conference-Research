# import streamlit as st

# st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
# st.sidebar.write("""
# A self-service app that automates the generation of biographical content 
# and assists in lead generation. Designed to support academic and professional 
# activities, it offers interconnected modules that streamline research tasks, 
# whether for conferences, campus visits, or other events.
# """)

# # Sidebar Info Box as Dropdown
# with st.sidebar.expander("Capabilities", expanded=False):
#     st.write("""
#     This app leverages cutting-edge technologies to automate and enhance research 
#     workflows. It combines generative AI, 
#     Retrieval-Augmented Generation (RAG), agentic RAG, and other advanced 
#     methodologies to deliver efficient and accurate results.

#     """)


# with st.sidebar:
#     st.markdown("# About This Tool")
#     st.markdown(
#        "We use multi-agent systems and other AI technologies to power this app."
#             )
#     st.markdown(
#        "This tool is a work in progress. "
#             )


# st.title('Conference and Campus Research Assistant') 

# st.markdown('Conduct your own research with the help of AI!') 


# st.info(
#     """**Ideas:** Editors  

# **Design and Development:** Natasha Newbold  

# Thank you to all contributors for your valuable input!""",
#     icon="ℹ️"
# )

# ### Background & Motivation

# with st.expander("Background"):
#   st.write('''
  
#   The **Conference and Campus Research Assistant** is an AI-powered research tool designed to automate and accelerate repetitive research tasks. Built with the needs of internal employees in mind, this tool helps streamline data collection, academic profile extraction, and outreach efforts.

#   Whether you are organizing a conference, conducting academic research, or engaging with potential collaborators, this tool provides an efficient way to gather, process, and analyze relevant data. It eliminates the need for manual searching, allowing you to focus on higher-level strategic work while AI handles the repetitive tasks.
  
#   ### Key Capabilities:
#   - **Biographical Content Generation (BioGen):** Automatically creates professional biographies from uploaded academic data.
#   - **Lead Generation (RAG):** Finds relevant academic contacts based on criteria like university affiliation and research focus.
#   - **Outreach Automation:** Generates personalized email drafts to engage with potential leads effectively.
#   - **Academic Profile Search (Desktop Research):** Enables fast lookup of researchers using local and online datasets.
#   - **PDF Data Extraction:** Extracts key information from uploaded research papers, conference programs, and academic CVs.
#   - **Course Catalogue & Reading List Management:** Helps organize and retrieve academic course details and reading materials.
#   - **Web Scraper for Academic Profiles:** Automates data extraction from university and research institution websites.
  
#   This tool is built with **Streamlit** and integrates AI-driven technologies to optimize research workflows, making it accessible and user-friendly for non-technical users.

  
#   *This application is continuously evolving. If you have feedback, feature requests, or encounter any issues, please contact the development team.*
  
# ''')
import streamlit as st
import base64

# Function to encode the image to base64
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Set page configuration
st.set_page_config(
    page_title="Conference & Campus Research Assistant",
    page_icon=":mortar_board:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a background image from local file path
background_image_path = "images/background.jpg"
background_image_base64 = get_base64_encoded_image(background_image_path)

st.markdown(
    f"""
    <style>
    .reportview-container {{
        background: url("data:image/jpeg;base64,{background_image_base64}") no-repeat center center fixed;
        background-size: cover;
    }}
    .sidebar .sidebar-content {{
        background-color: rgba(255, 255, 255, 0.9);
    }}
    .main {{
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 10px;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A self-service app that automates the generation of biographical content
and assists in lead generation. Designed to support academic and professional
activities, it offers interconnected modules that streamline research tasks,
whether for conferences, campus visits, or other events.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This app leverages cutting-edge technologies to automate and enhance research
    workflows. It combines generative AI, Retrieval-Augmented Generation (RAG),
    agentic RAG, and other advanced methodologies to deliver efficient and accurate results.
    """)

with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown("We use multi-agent systems and other AI technologies to power this app.")
    st.markdown("This tool is a work in progress.")

# Main content
st.title('Conference and Campus Research Assistant')
st.markdown('Conduct your own research with the help of AI!')

st.info(
    """**Ideas:** Editors

**Design and Development:** Natasha Newbold

Thank you to all contributors for your valuable input!""",
    icon="ℹ️"
)

# Background & Motivation
with st.expander("Background"):
    st.write('''
    The **Conference and Campus Research Assistant** is an AI-powered research tool designed to automate and accelerate repetitive research tasks. Built with the needs of internal employees in mind, this tool helps streamline data collection, academic profile extraction, and outreach efforts.

    Whether you are organizing a conference, conducting academic research, or engaging with potential collaborators, this tool provides an efficient way to gather, process, and analyze relevant data. It eliminates the need for manual searching, allowing you to focus on higher-level strategic work while AI handles the repetitive tasks.

    ### Key Capabilities:
    - **Biographical Content Generation (BioGen):** Automatically creates professional biographies from uploaded academic data.
    - **Lead Generation (RAG):** Finds relevant academic contacts based on criteria like university affiliation and research focus.
    - **Outreach Automation:** Generates personalized email drafts to engage with potential leads effectively.
    - **Academic Profile Search (Desktop Research):** Enables fast lookup of researchers using local and online datasets.
    - **PDF Data Extraction:** Extracts key information from uploaded research papers, conference programs, and academic CVs.
    - **Course Catalogue & Reading List Management:** Helps organize and retrieve academic course details and reading materials.
    - **Web Scraper for Academic Profiles:** Automates data extraction from university and research institution websites.

    This tool is built with **Streamlit** and integrates AI-driven technologies to optimize research workflows, making it accessible and user-friendly for non-technical users.

    *This application is continuously evolving. If you have feedback, feature requests, or encounter any issues, please contact the development team.*
    ''')

# Add some interactive elements
st.markdown("### Interactive Demo")
if st.button("Show Demo"):
    st.write("Here you can add a demo video or interactive widgets to showcase your app's capabilities.")

# Contact form
st.markdown("### Contact Us")
with st.form("contact_form"):
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    message = st.text_area("Your Message")
    submit_button = st.form_submit_button("Send Message")
    if submit_button:
        st.success("Thank you for your message! We will get back to you soon.")
