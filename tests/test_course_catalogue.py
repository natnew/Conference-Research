# ruff: noqa: I001
import contextlib
import json
import sys
import types

import pytest


# Minimal stubs for external dependencies so the module imports
class Sidebar(contextlib.AbstractContextManager):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def expander(self, *a, **k):
        return contextlib.nullcontext()

    def title(self, *a, **k):
        pass

    def write(self, *a, **k):
        pass


st = types.ModuleType("streamlit")
st.sidebar = Sidebar()
st.write = lambda *a, **k: None
st.markdown = lambda *a, **k: None
st.text_input = lambda *a, **k: ""
st.button = lambda *a, **k: False
st.spinner = lambda *a, **k: contextlib.nullcontext()
st.error = lambda *a, **k: None
st.warning = lambda *a, **k: None
st.info = lambda *a, **k: None
st.stop = lambda *a, **k: None
st.secrets = {}
sys.modules.setdefault("streamlit", st)

for name in [
    "selenium",
    "selenium.webdriver",
    "selenium.webdriver.chrome",
    "selenium.webdriver.chrome.options",
    "selenium.webdriver.chrome.service",
    "selenium.webdriver.common.by",
    "selenium.webdriver.support",
    "selenium.webdriver.support.ui",
    "selenium.webdriver.support.expected_conditions",
    "selenium.common.exceptions",
    "webdriver_manager.chrome",
    "webdriver_manager.core.os_manager",
    "bs4",
    "pandas",
    "requests",
    "duckduckgo_search",
]:
    sys.modules.setdefault(name, types.ModuleType(name))

sys.modules["selenium.webdriver.chrome.options"].Options = object
sys.modules["selenium.webdriver.chrome.service"].Service = object
sys.modules["selenium.webdriver.common.by"].By = object
sys.modules["selenium.webdriver.support.ui"].WebDriverWait = object
sys.modules["selenium.webdriver.support.expected_conditions"].EC = object
sys.modules["selenium.common.exceptions"].TimeoutException = Exception
sys.modules["selenium.common.exceptions"].ElementClickInterceptedException = Exception
sys.modules["webdriver_manager.chrome"].ChromeDriverManager = (
    lambda *a, **k: types.SimpleNamespace(install=lambda: "/tmp/chromedriver")
)
sys.modules["webdriver_manager.core.os_manager"].ChromeType = types.SimpleNamespace(
    CHROMIUM="chromium"
)
sys.modules["bs4"].BeautifulSoup = lambda *a, **k: None
sys.modules["pandas"].DataFrame = lambda *a, **k: None
sys.modules["requests"].exceptions = types.SimpleNamespace(
    RequestException=Exception, HTTPError=Exception
)


class DummyDDGS:
    def text(self, *a, **k):
        return []


sys.modules["duckduckgo_search"].DDGS = DummyDDGS

pydantic_mod = types.ModuleType("pydantic")


def Field(*_a, **_k):
    return None


class BaseModel:
    __annotations__: dict = {}

    def __init__(self, **data):
        for field in self.__annotations__:
            if field not in data:
                raise ValueError(f"missing field {field}")
        for k, v in data.items():
            setattr(self, k, v)

    @classmethod
    def model_validate_json(cls, json_str):
        return cls(**json.loads(json_str))


pydantic_mod.BaseModel = BaseModel
pydantic_mod.Field = Field
pydantic_mod.ValidationError = ValueError
sys.modules.setdefault("pydantic", pydantic_mod)

openai_mod = types.ModuleType("openai")


class OpenAI:
    def __init__(self):
        self.chat = types.SimpleNamespace(
            completions=types.SimpleNamespace(create=lambda *a, **k: None)
        )


openai_mod.OpenAI = OpenAI
openai_mod.OpenAIError = Exception
sys.modules.setdefault("openai", openai_mod)

from pages.Course_Catalogue import (
    CourseDetail,
    CoursePreview,
    extract_course_details,
    extract_courses,
)  # noqa: E402


@pytest.mark.unit
def test_extract_courses_parses_valid_json():
    client = types.SimpleNamespace()
    response_json = json.dumps({"courses": [{"course_name": "Math 101"}]})
    client.chat = types.SimpleNamespace(
        completions=types.SimpleNamespace(
            create=lambda *_a, **_k: types.SimpleNamespace(
                choices=[
                    types.SimpleNamespace(
                        message=types.SimpleNamespace(content=response_json)
                    )
                ]
            )
        )
    )
    result = extract_courses("dummy text", client)
    assert isinstance(result[0], CoursePreview)
    assert result[0].course_name == "Math 101"


@pytest.mark.unit
def test_extract_courses_handles_invalid_json():
    client = types.SimpleNamespace()
    client.chat = types.SimpleNamespace(
        completions=types.SimpleNamespace(
            create=lambda *_a, **_k: types.SimpleNamespace(
                choices=[
                    types.SimpleNamespace(
                        message=types.SimpleNamespace(content="not-json")
                    )
                ]
            )
        )
    )
    with pytest.raises(ValueError):
        extract_courses("dummy text", client)


@pytest.mark.unit
def test_extract_course_details_parses_valid_json():
    client = types.SimpleNamespace()
    detail_json = json.dumps(
        {
            "course_detail": {
                "course_name": "Math 101",
                "course_overview": "overview",
                "course_details": "details",
                "module_leader_name": "Dr X",
                "module_leader_email": "x@example.com",
            }
        }
    )
    client.chat = types.SimpleNamespace(
        completions=types.SimpleNamespace(
            create=lambda *_a, **_k: types.SimpleNamespace(
                choices=[
                    types.SimpleNamespace(
                        message=types.SimpleNamespace(content=detail_json)
                    )
                ]
            )
        )
    )
    detail = extract_course_details("Math 101", "text", client)
    assert isinstance(detail, CourseDetail)
    assert detail.course_name == "Math 101"


@pytest.mark.unit
def test_extract_course_details_handles_schema_mismatch():
    client = types.SimpleNamespace()
    bad_json = json.dumps({"invalid": True})
    client.chat = types.SimpleNamespace(
        completions=types.SimpleNamespace(
            create=lambda *_a, **_k: types.SimpleNamespace(
                choices=[
                    types.SimpleNamespace(
                        message=types.SimpleNamespace(content=bad_json)
                    )
                ]
            )
        )
    )
    with pytest.raises(ValueError):
        extract_course_details("Math 101", "text", client)
