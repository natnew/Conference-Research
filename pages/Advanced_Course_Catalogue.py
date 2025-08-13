"""Advanced Course Catalogue page using Crawl4AI for web crawling.

This page extends the original course catalogue by leveraging Crawl4AI to
fetch course information. It combines course and university inputs to build a
more precise search query.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import streamlit as st
from duckduckgo_search import DDGS

try:  # pragma: no cover - handled in tests
    from crawl4ai import WebCrawler
except ModuleNotFoundError:  # pragma: no cover
    WebCrawler = None  # type: ignore[assignment]

from pages.Course_Catalogue import extract_courses


@dataclass
class CourseCrawler:
    """Wrapper around Crawl4AI's :class:`WebCrawler`.

    The crawler fetches the raw HTML content for a given URL.
    """

    crawler: WebCrawler | None = field(init=False)

    def __post_init__(self) -> None:
        self.crawler = WebCrawler() if WebCrawler else None

    def fetch(self, url: str) -> str:
        """Return the HTML content for ``url`` using Crawl4AI."""

        if not self.crawler:
            raise RuntimeError(
                "crawl4ai is not installed. Please install crawl4ai to use this feature."
            )
        result = self.crawler.crawl(url)
        return result.get("html", "")


def build_search_query(course: str, university: str) -> str:
    """Construct a combined search query for DuckDuckGo."""

    return f"{course} {university} course catalogue"


def crawl_from_query(course: str, university: str, crawler: CourseCrawler) -> str:
    """Search DuckDuckGo and crawl the first result using ``crawler``.

    Parameters
    ----------
    course:
        Name of the course.
    university:
        Name of the university.
    crawler:
        Instance of :class:`CourseCrawler` used to fetch page content.

    Returns
    -------
    str
        HTML content of the first search result or an empty string when no
        results are available.
    """

    query = build_search_query(course, university)
    ddgs = DDGS()
    results = list(ddgs.text(query, max_results=1))
    if not results:
        return ""
    url = results[0]["href"]
    return crawler.fetch(url)


def main() -> None:
    """Streamlit UI entry point for the advanced course catalogue."""

    st.title("Advanced Course Catalogue")
    if WebCrawler is None:
        st.error("crawl4ai is not installed. Please install crawl4ai to use this page.")
        return
    course = st.text_input("Course name")
    university = st.text_input("University")
    if st.button("Search"):
        crawler = CourseCrawler()
        html = crawl_from_query(course, university, crawler)
        if not html:
            st.info("No results found.")
            return
        try:
            with st.spinner("Extracting courses..."):
                client = None  # Replace with a real OpenAI client in production
                client_html = extract_courses(html, client)
            st.write(client_html)
        except Exception as exc:  # pragma: no cover - Streamlit display
            st.error(f"Failed to extract courses: {exc}")


if __name__ == "__main__":
    main()
