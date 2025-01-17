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
    """
    Fetch the reading list for the specified university and course. The query is refined to return books, recommended_resources, sources_info
    from a professional perspective and includes references to books, articles, and lecture materials.
    Books are categorized as the reading list, while articles and lecture materials are categorized as recommended resources.
    """
    """
    Fetch the reading list for the specified university and course. The query is refined to return results
    from a professional perspective and includes references to books, articles, and lecture materials.
    """
    query = f"You are a course professional with provided details of a {university}, and the interested {course}. Please provide a detailed reading list, categorizing books as the 'Reading List' and articles or lecture materials as 'Recommended Resources' with their links if present."
    results = DDGS().chat(query, model="claude-3-haiku")
    if results:
        books = [item for item in results if 'book' in item.lower()]
        recommended_resources = [item for item in results if 'article' in item.lower() or 'lecture' in item.lower()]
        sources_info = "The information is retrieved from DuckDuckGo searches, which includes publicly available resources and AI recommendations. Books are presented as the 'Reading List,' and articles or lecture materials provided are shown as 'Recommended Resources.' from the AI "
        return books, recommended_resources, sources_info
        sources_info = "The information is retrieved from DuckDuckGo searches, which includes publicly available resources with AI recommendations. Professional resources are prioritized."
        return results, sources_info
        return results
    else:
        return "No results found. Please try a different query.", ""


def main():
    st.title("Course Reading List")
    
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
                books, recommended_resources, sources_info = get_reading_list(university, course)
                st.write("### Reading List")
                if books:
                    for book in books:
                        st.write(f"- {book}")
                else:
                    st.write("No books found in the reading list.")

                st.write("### Recommended Resources")
                if recommended_resources:
                    for resource in recommended_resources:
                        st.write(f"- {resource}")
                else:
                    st.write("No recommended resources found.")
                st.info("Information Source: " + sources_info)
                st.write("#### Reading List")
                if isinstance(results, list):
                    for item in results:
                        st.write(f"- {item}")
                else:
                    st.write(results)
            else:
                st.warning("Please provide both the University Name and Course Name.")

if __name__ == "__main__":
    main()


# # Function to fetch the reading list using DuckDuckGo

# def get_reading_list(university: str, course: str):
#     query = f"You are a course professional with the  following {university}, {course} please give me a suitable   reading list  which includes books, peer-reviewed articles, and lecture materials from the university with their links"
#     results = DDGS().chat(query, model="claude-3-haiku")
#     if results:
#         sources_info = "The information is retrieved from DuckDuckGo searches, which includes publicly available resources data and AI recommendations."
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
#                 st.write("### Recommended Resources")
#                 st.info("Information Source: " + sources_info)
#                 st.write("### Reading List")
#                 if isinstance(results, list):
#                     for item in results:
#                         st.write(f"- {item}")
#                 else:
#                     st.write(results)
#             else:
#                 st.warning("Please provide both the University Name and Course Name.")

# if __name__ == "__main__":
#     main()

