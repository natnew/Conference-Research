import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
from io import BytesIO

BASE_URL = "https://coms.events/epsa2025/"
BROWSE_URL = urljoin(BASE_URL, "en/browse.html")

def fetch_soup(url):
    r = requests.get(url)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def get_all_session_links(browse_url):
    soup = fetch_soup(browse_url)
    session_links = set()
    for a in soup.select('a[href*="data/sessions/en/session_"]'):
        href = a.get('href')
        if href:
            session_links.add(urljoin(browse_url, href))
    return session_links

def extract_presenters_from_session(session_url):
    soup = fetch_soup(session_url)
    presenters = []
    # Each paper row has a <div class="authors">
    for author_div in soup.find_all("div", class_="authors"):
        # One or more presenters
        for span in author_div.find_all("span", class_="presenter"):
            name = span.get_text(strip=True)
            # Affiliation is the text **immediately following** the presenter span
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

def scrape_all_presenters():
    all_presenters = []
    session_links = get_all_session_links(BROWSE_URL)
    for i, session_url in enumerate(session_links, 1):
        presenters = extract_presenters_from_session(session_url)
        all_presenters.extend(presenters)
        # Progress display in Streamlit
        st.info(f"Scraped {i} / {len(session_links)} session pages…")
    return all_presenters

# --- STREAMLIT APP ---
def main():
    st.title("EPSA 2025 Presenter Scraper (All Sessions, All Days)")
    st.info("This tool scrapes all session pages from the EPSA 2025 conference, extracting presenter names and their affiliations.")

    if st.button("Scrape EPSA 2025 Presenters"):
        with st.spinner("Scraping in progress..."):
            data = scrape_all_presenters()
            if not data:
                st.warning("No presenters found. The site structure may have changed.")
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
                "epsa2025_presenters.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    main()
