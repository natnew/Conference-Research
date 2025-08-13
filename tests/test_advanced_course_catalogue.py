import importlib
import sys
import types

import pytest

# NOTE: Advanced_Course_Catalogue page is currently DISABLED.
# These tests are adapted to assert the disabled notice instead of crawl4ai dependency behavior.


@pytest.mark.unit
def test_disabled_page_shows_notice(monkeypatch):
    sys.modules.pop("pages.Advanced_Course_Catalogue", None)
    page = importlib.import_module("pages.Advanced_Course_Catalogue")
    captured = {}
    monkeypatch.setattr(page.st, "title", lambda *_a, **_k: None)
    monkeypatch.setattr(page.st, "info", lambda msg: captured.setdefault("info", msg))
    page.main()
    assert "disabled" in captured["info"].lower()
