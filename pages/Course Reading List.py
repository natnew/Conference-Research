import streamlit as st
from duckduckgo_search import DDGS

# Function to fetch the reading list using DuckDuckGo

def get_reading_list(university: str, course: str):
    query = f"{university}, {course} reading list with links"
    results = DDGS().chat(query, model="claude-3-haiku")
    if results:
        return results
    else:
        return "No results found. Please try a different query."


def main():
    st.title("Course Reading List")
    
    st.write("""### Course Materials
    This page provides access to recommended or required reading lists for university courses.
    Enter the details below to get the full list.
    """)
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
                results = get_reading_list(university, course)
                st.write("### Reading List")
                st.write(results)
            else:
                st.warning("Please provide both the University Name and Course Name.")

if __name__ == "__main__":
    main()

