import streamlit as st
from duckduckgo_search import DDGS


# Sidebar content
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
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


# Function to fetch the reading list using DuckDuckGo

def get_reading_list(university: str, course: str):
    query = f"""Generate a detailed reading list for {course} at {university}. Include only:

            1. Core Textbooks (3-5):
            - Title, author, edition,publisher, year
            - Direct link to publisher/retailer
            - Brief description of coverage (2-3 sentences)
            
            2. Recommended Essential  Articles (5-7):
            - Full citation (author, title, journal, year, volume, issue, pages)
            - DOI or stable URL
            - Key takeaways (1-2 sentences)
            
            3. Recommended Supplementary Resources:
            - Online lecture notes/videos if available
            - Relevant academic papers
            - Practice problems/workbooks
            - Direct link to these resources
            
            Format the response as a clean list without any introductory text or concluding remarks.
            Ensure that URLs provided are not fabricated. If a stable URL or DOI is not available, leave the field empty
            Do not include phrases like "here is" or "comprehensive" or "please note".
            Simply start with the content directly."""
    results = DDGS().chat(query, model="claude-3-haiku")
    if results:
        sources_info = "The information is retrieved from DuckDuckGo searches, which includes publicly available resources data and AI recommendations on supporting materials like articles and supplementary lecture materials."
        return results, sources_info
        return results
    else:
        return "No results found. Please try a different query.", ""


def main():
    st.title("Course Reading List")
    
    #University name Input Text Field
    university = st.text_input(
        "University Name",
        placeholder="e.g., Harvard Law School"
    )
    #Course Name Input text field
    course = st.text_input(
        "Course Name",
        placeholder="e.g., Criminal Law"
    )
    
    if st.button("Get Reading List"):
        with st.spinner("Fetching reading list..."):
            if university and course:
                results, sources_info = get_reading_list(university, course)
                st.info("Information Source: " + sources_info)
                st.write("### Reading List with recommended supporting materials")
                if isinstance(results, list):
                    for item in results:
                        st.write(f"- {item}")
                else:
                    st.write(results)
            else:
                st.warning("Please provide both the University Name and Course Name.")

if __name__ == "__main__":
    main()
