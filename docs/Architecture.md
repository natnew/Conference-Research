# Architecture Overview

The Conference Research app is built with a modular design. The backend
leverages Python modules for scraping, searching and email generation while the
frontend uses Streamlit for a multipage interface.

```
+---------------+       +-------------------+
|  Streamlit UI | <---> |  Backend Modules  |
+---------------+       +-------------------+
        |                        |
        v                        v
  Data Storage            External Services
```

- **Backend Modules**: Located under `con_research/src/modules`, these handle
  web scraping, semantic search, and email generation.
- **Streamlit Pages**: Found in the project root and `pages/` directory. Each
  page focuses on a specific workflow such as bio generation or outreach.
- **Data Storage**: Results are cached locally and can be saved to spreadsheets.
- **External Services**: Includes search APIs and the Groq API for internet
  queries.

This design allows new pages or modules to be added without impacting existing
functionality.

