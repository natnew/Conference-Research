# import streamlit as st
# from duckduckgo_search import DDGS


# # Sidebar content
# st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
# st.sidebar.write("""
# A dedicated tool to help students and educators retrieve and summarize reading lists for
# university courses. The tool combines AI and web search to provide comprehensive
# information on books, articles, and lecture materials related to specific courses.
# """)

# # Sidebar Info Box as Dropdown
# with st.sidebar.expander("Capabilities", expanded=False):
#     st.write("""
#     This tool provides the following advanced capabilities:
#     - AI-driven retrieval of books, articles, and lecture materials
#     - User-friendly interface for customized queries
#     - Support for fetching course-specific reading lists with source links
#     - Efficient use of DuckDuckGo for search results
#     """)

# with st.sidebar:
#     st.markdown("# About This Tool")
#     st.markdown(
#         "This application enables users to access detailed reading lists for university courses. "
#         "It retrieves books, articles, and lecture materials using AI and web search. "
#         "The tool is ideal for educators, students, and researchers looking for quick access to structured "
#         "course reading materials and sources."
#     )
#     st.markdown(
#         "The tool is continuously improved to enhance its search accuracy and relevance. "
#         "Your feedback helps us deliver better results."
#     )


# # Function to fetch the reading list using DuckDuckGo

# def get_reading_list(university: str, course: str):
#     query = f"""Generate a detailed reading list for {course} at {university}. Include only:

#             1. Core Textbooks (3-5):
#             - Title, author, edition,publisher, year
#             - Direct link to publisher/retailer
#             - Brief description of coverage (2-3 sentences)
            
#             2. Recommended Essential  Articles (5-7):
#             - Full citation (author, title, journal, year, volume, issue, pages)
#             - DOI or stable URL
#             - Key takeaways (1-2 sentences)
            
#             3. Recommended Supplementary Resources:
#             - Online lecture notes/videos if available
#             - Relevant academic papers
#             - Practice problems/workbooks
#             - Direct link to these resources
            
#             Format the response as a clean list without any introductory text or concluding remarks.
#             Do not include phrases like "here is" or "comprehensive" or "please note".
#             Simply start with the content directly."""
#     results = DDGS().chat(query, model="claude-3-haiku")
#     if results:
#         sources_info = "The information is retrieved from DuckDuckGo searches, which includes publicly available resources data and AI recommendations on supporting materials like articles and supplementary lecture materials."
#         return results, sources_info
#         return results
#     else:
#         return "No results found. Please try a different query.", ""


# def main():
#     st.title("Course Reading List")
    
#     #University name Input Text Field
#     university = st.text_input(
#         "University Name",
#         placeholder="e.g., Harvard Law School"
#     )
#     #Course Name Input text field
#     course = st.text_input(
#         "Course Name",
#         placeholder="e.g., Criminal Law"
#     )
    
#     if st.button("Get Reading List"):
#         with st.spinner("Fetching reading list..."):
#             if university and course:
#                 results, sources_info = get_reading_list(university, course)
#                 st.info("Information Source: " + sources_info)
#                 st.write("### Reading List with recommended supporting materials")
#                 if isinstance(results, list):
#                     for item in results:
#                         st.write(f"- {item}")
#                 else:
#                     st.write(results)
#             else:
#                 st.warning("Please provide both the University Name and Course Name.")

# if __name__ == "__main__":
#     main()

import streamlit as st
from duckduckgo_search import DDGS
import json
import re

# Sidebar content
st.sidebar.title(":books: Conference & Campus Research Assistant")
st.sidebar.write("""
A dedicated tool to help students and educators retrieve and summarize reading lists for
university courses. The tool combines AI and web search to provide comprehensive
information on books, articles, and lecture materials related to specific courses.
""")

# Sidebar Info Box as Dropdown
with st.sidebar.expander("Capabilities", expanded=False):
    st.write("""
    This tool provides the following advanced capabilities:
    - AI-driven retrieval of books, articles, and lecture materials
    - User-friendly interface for customized queries
    - Support for fetching course-specific reading lists with source links
    - Efficient use of DuckDuckGo for search results
    """)

with st.sidebar:
    st.markdown("# About This Tool")
    st.markdown(
        "This application enables users to access detailed reading lists for university courses. "
        "It retrieves books, articles, and lecture materials using AI and web search. "
        "The tool is ideal for educators, students, and researchers looking for quick access to structured "
        "course reading materials and sources."
    )
    st.markdown(
        "The tool is continuously improved to enhance its search accuracy and relevance. "
        "Your feedback helps us deliver better results."
    )

# Configuration: Mapping institutions to their reading list URLs
INSTITUTION_READING_LISTS = {
    "Harvard Law School": "https://harvardlawschool.edu/course-reading-lists",
    "Stanford University": "https://stanford.edu/reading-lists",
    # Add more institutions and their reading list URLs here
}

# Function to fetch the reading list from centralized storage
def fetch_reading_list_from_storage(university: str, course: str):
    # This function should be implemented to fetch reading lists from actual storage
    # For demonstration, we'll return None to indicate no centralized reading list is available
    return None

# Function to perform a DuckDuckGo search and retrieve the first valid URL
def get_valid_url(query: str):
    with DDGS() as ddgs:
        results = ddgs.text(query, region='wt-wt', safesearch='off', time='y', max_results=5)
        for result in results:
            url = result.get('href') or result.get('url')
            if url and re.match(r'^https?:\/\/', url):
                return url
    return "URL not found."

# Function to fetch the reading list using AI and validate URLs
def get_reading_list(university: str, course: str):
    # First, attempt to fetch from centralized storage
    reading_list = fetch_reading_list_from_storage(university, course)
    sources_info = ""
    if reading_list:
        sources_info = f"Retrieved from centralized storage: {INSTITUTION_READING_LISTS.get(university, 'N/A')}"
        return reading_list, sources_info
    else:
        # If not available, generate using AI and web search
        query = f"""
Generate a detailed reading list for the course "{course}" at {university}. Include only:

1. Core Textbooks (3-5):
- Title
- Author
- Edition
- Publisher
- Year
- Volume
- Brief description of coverage (2-3 sentences)

2. Recommended Essential Articles (5-7):
- Full citation (author, title, journal, year, volume, issue, pages)
- DOI or stable URL
- Key takeaways (1-2 sentences)

3. Recommended Supplementary Resources:
- Online lecture notes/videos if available
- Relevant academic papers
- Practice problems/workbooks
- Direct link to these resources

Format the response as a JSON object with the following structure:

{
    "Core Textbooks": [
        {
            "Title": "",
            "Author": "",
            "Edition": "",
            "Publisher": "",
            "Year": "",
            "Volume": "",
            "Description": ""
        },
        ...
    ],
    "Essential Articles": [
        {
            "Citation": "",
            "DOI": "",
            "Key Takeaways": ""
        },
        ...
    ],
    "Supplementary Resources": [
        {
            "Resource Type": "",
            "Title": "",
            "URL": ""
        },
        ...
    ]
}

Ensure that URLs are not fabricated. If a stable URL or DOI is not available, leave the field empty.
"""
        # Call the AI model (assuming DDGS().chat is correctly set up)
        results = DDGS().chat(query, model="claude-3-haiku")
        if results:
            try:
                reading_list = json.loads(results)
                # Validate and retrieve URLs if necessary
                # For Core Textbooks and Essential Articles, ensure URLs are valid
                for textbook in reading_list.get("Core Textbooks", []):
                    if not textbook.get("Publisher URL"):
                        search_query = f"{textbook['Title']} {textbook['Author']} publisher"
                        textbook["Publisher URL"] = get_valid_url(search_query)
                for article in reading_list.get("Essential Articles", []):
                    if not article.get("DOI") or not re.match(r'^https?:\/\/', article['DOI']):
                        search_query = f"{article['Citation']} DOI"
                        article["DOI"] = get_valid_url(search_query)
                for resource in reading_list.get("Supplementary Resources", []):
                    if not resource.get("URL"):
                        search_query = f"{resource['Title']} {resource['Resource Type']}"
                        resource["URL"] = get_valid_url(search_query)
                sources_info = "Information retrieved from DuckDuckGo searches and AI-generated content."
                return reading_list, sources_info
            except json.JSONDecodeError:
                return "Failed to parse the reading list. Please try again.", ""
        else:
            return "No results found. Please try a different query.", ""

def main():
    st.title("📚 Course Reading List")

    # University name Input Text Field
    university = st.text_input(
        "University Name",
        placeholder="e.g., Harvard Law School"
    )
    # Course Name Input text field
    course = st.text_input(
        "Course Name",
        placeholder="e.g., Criminal Law"
    )

    if st.button("Get Reading List"):
        with st.spinner("Fetching reading list..."):
            if university and course:
                results, sources_info = get_reading_list(university, course)
                st.info("Information Source: " + sources_info)
                if isinstance(results, dict):
                    # Display Core Textbooks
                    st.subheader("Core Textbooks")
                    for idx, textbook in enumerate(results.get("Core Textbooks", []), 1):
                        st.markdown(f"**{idx}. {textbook['Title']}**")
                        st.write(f"*Author:* {textbook['Author']}")
                        st.write(f"*Edition:* {textbook['Edition']}")
                        st.write(f"*Publisher:* {textbook['Publisher']} ({textbook['Year']})")
                        st.write(f"*Volume:* {textbook['Volume']}")
                        st.write(f"*Description:* {textbook['Description']}")
                        if textbook.get("Publisher URL") and textbook["Publisher URL"] != "URL not found.":
                            st.markdown(f"[Publisher Link]({textbook['Publisher URL']})")
                        else:
                            st.write("Publisher URL: Not Available")
                        st.markdown("---")

                    # Display Essential Articles
                    st.subheader("Recommended Essential Articles")
                    for idx, article in enumerate(results.get("Essential Articles", []), 1):
                        st.markdown(f"**{idx}. {article['Citation']}**")
                        st.write(f"*DOI/URL:* {article['DOI'] if article.get('DOI') else 'Not Available'}")
                        st.write(f"*Key Takeaways:* {article['Key Takeaways']}")
                        st.markdown("---")

                    # Display Supplementary Resources
                    st.subheader("Recommended Supplementary Resources")
                    for idx, resource in enumerate(results.get("Supplementary Resources", []), 1):
                        st.markdown(f"**{idx}. {resource['Title']}**")
                        st.write(f"*Resource Type:* {resource['Resource Type']}")
                        if resource.get("URL") and resource["URL"] != "URL not found.":
                            st.markdown(f"[Access Resource]({resource['URL']})")
                        else:
                            st.write("Resource URL: Not Available")
                        st.markdown("---")
                elif isinstance(results, str):
                    st.error(results)
                else:
                    st.write(results)
            else:
                st.warning("Please provide both the University Name and Course Name.")

if __name__ == "__main__":
    main()
