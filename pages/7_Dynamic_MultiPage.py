import streamlit as st
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from bs4 import BeautifulSoup
from io import BytesIO

# Assuming you have a get_chrome_driver() function as in your existing codebase
# from your_existing_module import get_chrome_driver

def dynamic_scrape_epsa2025(start_url, max_depth=3, wait_time=4):
    """
    Recursively scrape all names and universities from the EPSA 2025 conference site.
    """
    driver = get_chrome_driver()
    visited = set()
    data = []

    def extract_people_from_html(html):
        soup = BeautifulSoup(html, 'html.parser')
        rows = []
        # The relevant participant data is often in tables or lists
        # Try to find all speaker/participant/author names and affiliations
        # Adjust these selectors as necessary for different conference layouts

        # Example: For EPSA 2025 abstracts, names and affiliations are inside <div class="author">
        for author_block in soup.find_all('div', class_='author'):
            name = author_block.find('span', class_='authorName')
            affiliation = author_block.find('span', class_='authorAffiliation')
            if name:
                rows.append({
                    "Name": name.text.strip(),
                    "Affiliation": (affiliation.text.strip() if affiliation else "")
                })
        # Fallback for alternative structures: Find <table> with names and affiliations
        for tr in soup.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 2:
                rows.append({
                    "Name": tds[0].text.strip(),
                    "Affiliation": tds[1].text.strip()
                })
        return rows

    def collect_links(html, base_url):
        # For EPSA 2025, links to sessions/abstracts are under <a> tags with /epsa2025/ in href
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if ('/epsa2025/' in href or '/abstracts/' in href or '/sessions/' in href) and not href.endswith('index.html'):
                # Make absolute URL if necessary
                if href.startswith('http'):
                    links.add(href)
                else:
                    links.add(base_url.rstrip('/') + '/' + href.lstrip('/'))
        return links

    def scrape_recursive(url, depth):
        if url in visited or depth > max_depth:
            return
        visited.add(url)
        try:
            driver.get(url)
            time.sleep(wait_time)
            # Accept cookie banner if present
            try:
                cookie_btns = [
                    "//button[contains(text(), 'Accept')]",
                    "//button[contains(text(), 'accept')]",
                    "//button[contains(@class, 'accept')]",
                    "//button[contains(text(), 'Allow')]",
                    "//button[contains(text(), 'Agree')]",
                ]
                for btn in cookie_btns:
                    try:
                        WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, btn))
                        ).click()
                        time.sleep(1)
                        break
                    except (TimeoutException, ElementClickInterceptedException, NoSuchElementException):
                        continue
            except Exception:
                pass

            html = driver.page_source
            # Extract participants from this page
            extracted = extract_people_from_html(html)
            data.extend(extracted)

            # Find and scrape sub-links recursively
            new_links = collect_links(html, base_url=start_url)
            for lnk in new_links:
                if lnk not in visited:
                    scrape_recursive(lnk, depth + 1)
        except Exception as e:
            st.warning(f"Failed at {url}: {e}")

    # Begin scraping
    scrape_recursive(start_url, 0)
    driver.quit()
    return data

def main():
    st.title("Dynamic Multi-Page Conference Scraper")
    st.write("""
    This tool scrapes the EPSA 2025 conference site, delving down through all relevant subpages to extract all participant names and university affiliations.
    """)
    default_url = "https://coms.events/epsa2025/index.html"
    url = st.text_input("Enter start URL:", value=default_url)
    wait_time = st.slider("Wait time for page load (seconds):", 2, 10, 4)
    max_depth = st.slider("Maximum recursion depth:", 1, 5, 3, help="Set this to limit how deep the scraper explores linked pages.")

    if st.button("Scrape Conference Site"):
        with st.spinner("Scraping in progress. This may take a few minutes..."):
            all_data = dynamic_scrape_epsa2025(url, max_depth=max_depth, wait_time=wait_time)
            if all_data:
                df = pd.DataFrame(all_data)
                st.success(f"Scraping complete. Extracted {len(df)} entries.")
                st.dataframe(df)
                # Download as Excel
                output = BytesIO()
                df.to_excel(output, index=False, engine='openpyxl')
                output.seek(0)
                st.download_button(
                    "Download Results as Excel",
                    output,
                    "epsa2025_participants.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key='download-excel'
                )
            else:
                st.warning("No participant data found. The page structure may have changed, or further selector tuning is needed.")

if __name__ == "__main__":
    main()
