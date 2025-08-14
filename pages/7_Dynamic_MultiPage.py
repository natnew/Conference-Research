"""
Dynamic MultiPage - Automated Conference Session Scraper
=======================================================

A specialized Streamlit web scraping tool for automatically navigating and extracting
academic information from multi-page conference websites. Excels at handling complex
conference sites with multiple session pages and bulk presenter extraction.

KEY FEATURES:
- Autonomous multi-page navigation and session link discovery
- Pattern-based session page identification and bulk extraction
- Affiliation parsing with progress tracking for large sites
- Excel export with session-organized data and error handling

REQUIREMENTS:
- Dependencies: streamlit, requests, beautifulsoup4, pandas, urllib.parse
- Input: Conference URL with session listings and consistent HTML structure

TECHNICAL ARCHITECTURE:
- Link Discovery: Scans index pages, pattern matching, URL validation
- Extraction Pipeline: Parse index → collect links → extract per session → compile data

WORKFLOW:
1. Input conference URL → 2. Scan for session links → 3. Validate URLs
4. Process each session → 5. Extract names/affiliations → 6. Compile dataset → 7. Export

EXTRACTION PATTERNS (Configurable):
- Session links: "session_*.html", Presenter container: <div class="authors">
- Presenter element: <span class="presenter">, Affiliation: Following text

USE CASES:
- Conference participant database creation and networking preparation
- Research collaboration identification and contact compilation
- Academic community mapping and event planning coordination
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from io import BytesIO

# Sidebar content
st.sidebar.title(":streamlit: Conference & Campus Research Assistant")
st.sidebar.write("""
A specialized web scraping tool designed to extract academic profiles from conference
websites and institutional pages. Automatically identifies and extracts names,
affiliations, and other relevant information while handling dynamic content and
cookie consents.
""")

def fetch_soup(url):
    r = requests.get(url)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def get_all_session_links(browse_url):
    soup = fetch_soup(browse_url)
    session_links = set()
    # Collect all links that look like session pages (adjust pattern as needed)
    for a in soup.find_all("a", href=True):
        href = a['href']
        # Generic pattern: adjust 'session_' as required for other sites
        if "session_" in href and href.endswith('.html'):
            session_links.add(urljoin(browse_url, href))
    return session_links

def extract_presenters_from_session(session_url):
    soup = fetch_soup(session_url)
    presenters = []
    # Assumes presenters are within <div class="authors">
    for author_div in soup.find_all("div", class_="authors"):
        for span in author_div.find_all("span", class_="presenter"):
            name = span.get_text(strip=True)
            # Affiliation is the text immediately after the <span class="presenter">
            next_node = span.next_sibling
            affiliation = ""
            while next_node:
                if hasattr(next_node, "text"):
                    affiliation += next_node.text
                elif isinstance(next_node, str):
                    affiliation += next_node
                next_node = next_node.next_sibling
            affiliation = affiliation.strip(" ,")
            presenters.append({
                "Name": name,
                "Affiliation": affiliation,
                "Session Page": session_url
            })
    return presenters

def scrape_all_presenters(browse_url):
    all_presenters = []
    try:
        session_links = get_all_session_links(browse_url)
    except Exception as e:
        st.error(f"Failed to retrieve session links from the page: {e}")
        return []
    for i, session_url in enumerate(session_links, 1):
        try:
            presenters = extract_presenters_from_session(session_url)
            all_presenters.extend(presenters)
            st.info(f"Scraped {i} / {len(session_links)} session pages…")
        except Exception as e:
            st.warning(f"Could not scrape session: {session_url}. Error: {e}")
    return all_presenters

def main():
    st.title("Dynamic MultiPage Scraper")
    st.info(
        "Enter the URL of a conference 'Browse' or session directory page. "
        "This tool will find all session pages and extract all presenter names and affiliations. "
        "It works for conferences structured like EPSA 2025."
    )
    example = "https://coms.events/epsa2025/en/browse.html"
    browse_url = st.text_input("Enter the Browse/Directory URL:", value=example)

    if st.button("Scrape Presenters"):
        with st.spinner("Scraping in progress..."):
            data = scrape_all_presenters(browse_url)
            if not data:
                st.warning("No presenters found. Either the URL is incorrect, or the page structure is unsupported.")
                return
            df = pd.DataFrame(data)
            st.success(f"Scraping complete. {len(df)} presenter records found.")
            st.dataframe(df)
            # Download button
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            st.download_button(
                "Download as Excel",
                output,
                "conference_presenters.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()