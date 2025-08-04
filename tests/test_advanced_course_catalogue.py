import sys
import types

import pytest

# Stub external modules before importing the page
crawl4ai_mod = types.ModuleType("crawl4ai")


class DummyWebCrawler:
    def __init__(self):
        self.calls = []

    def crawl(self, url):
        self.calls.append(url)
        return {"html": "<html>content</html>"}


crawl4ai_mod.WebCrawler = DummyWebCrawler
sys.modules.setdefault("crawl4ai", crawl4ai_mod)

duckduckgo_mod = types.ModuleType("duckduckgo_search")
duckduckgo_mod.DDGS = object
sys.modules.setdefault("duckduckgo_search", duckduckgo_mod)

from pages.Advanced_Course_Catalogue import (  # noqa: E402
    CourseCrawler,
    build_search_query,
    crawl_from_query,
)


@pytest.mark.unit
def test_build_search_query_combines_course_and_university():
    result = build_search_query("Math", "Oxford")
    assert result == "Math Oxford course catalogue"


@pytest.mark.unit
def test_course_crawler_fetch_returns_html():
    crawler = CourseCrawler()
    html = crawler.fetch("https://example.com")
    assert html == "<html>content</html>"


@pytest.mark.unit
def test_crawl_from_query_uses_ddgs_and_crawler(monkeypatch):
    class DummyDDGS:
        def text(self, *a, **k):
            return [{"href": "https://example.com"}]

    monkeypatch.setattr(
        "pages.Advanced_Course_Catalogue.DDGS", lambda: DummyDDGS()
    )
    crawler = CourseCrawler()
    html = crawl_from_query("Math", "Oxford", crawler)
    assert html == "<html>content</html>"
