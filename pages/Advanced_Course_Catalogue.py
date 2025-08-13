"""Advanced Course Catalogue (DISABLED)

This page has been temporarily disabled to remove the optional crawl4ai/playwright
dependency that was causing installation failures and slow builds.

To re-enable:
1. Add crawl4ai and playwright back to requirements / pyproject.
2. Restore the previous implementation from version control.
3. Ensure Chromium/Playwright install step runs before Streamlit startup.
"""

import streamlit as st


def main():  # pragma: no cover
    st.title("Advanced Course Catalogue (Disabled)")
    st.info(
        "This experimental page is disabled to stabilise dependency installation. "
        "Remove this placeholder and restore the original file to re-enable it."
    )


if __name__ == "__main__":  # pragma: no cover
    main()
