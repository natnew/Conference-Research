import sys
import types
from urllib.error import URLError
from unittest.mock import patch

# Create a dummy imports module to satisfy dependencies
imports_stub = types.ModuleType('imports')

import urllib.request
from io import BytesIO, StringIO

# minimal stubs required by scrapping_module
imports_stub.urllib = urllib
imports_stub.BytesIO = BytesIO
imports_stub.StringIO = StringIO

class Dummy:
    pass
imports_stub.PDFResourceManager = Dummy
imports_stub.PDFPageInterpreter = Dummy
imports_stub.TextConverter = Dummy
imports_stub.LAParams = Dummy
class DummyPDFPage:
    @staticmethod
    def get_pages(*args, **kwargs):
        return []
imports_stub.PDFPage = DummyPDFPage

imports_stub.requests = types.SimpleNamespace(get=lambda *a, **k: types.SimpleNamespace(status_code=404, text=''))
imports_stub.BeautifulSoup = lambda text, parser: types.SimpleNamespace(get_text=lambda separator=' ', strip=True: '')
imports_stub.BaseModel = type('BaseModel', (), {})
imports_stub.Field = lambda *a, **k: None
imports_stub.webdriver = types.SimpleNamespace(Chrome=object)
imports_stub.By = types.SimpleNamespace(TAG_NAME='body', CSS_SELECTOR='css')
imports_stub.Options = type('Options', (), {'add_argument': lambda self, arg: None})
from typing import Optional, Type, Any
imports_stub.Optional = Optional
imports_stub.Type = Type
imports_stub.Any = Any

sys.modules['con_research.src.modules.imports'] = imports_stub

from con_research.src.modules.scrapping_module import ContentScraper


def test_extract_text_valid_scheme_http():
    with patch('urllib.request.urlopen', side_effect=URLError('no network')):
        result = ContentScraper._extract_text_from_pdf_url('http://example.com/file.pdf')
    assert result.startswith('Failed to retrieve the PDF document')


def test_extract_text_invalid_scheme():
    result = ContentScraper._extract_text_from_pdf_url('ftp://example.com/file.pdf')
    assert 'Invalid URL scheme' in result
