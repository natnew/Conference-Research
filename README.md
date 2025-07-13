# Conference Research

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Conduct your own conference research in a few simple steps!

This repository contains a Streamlit application for generating short
biographies, searching conference material and crafting outreach emails.

## Table of Contents
1. [Project Overview](#project-overview)
2. [Streamlit Pages](#streamlit-pages)
3. [Setup](#-setup)
4. [Usage](#usage)
5. [Documentation](#documentation)
6. [License](#license)

## Project Overview
💡 The app automates biographical data collection and lead generation through a series of Streamlit pages.

Key features include:
- Upload a PDF or URL with conference attendees' names.
- Agents scrape the web for participant bios and store them locally.
- Filter names by geographic region or university and select delegates based on their bios.
- Craft personalised outreach emails with AI templates.

## Presentation
### 📹 Video 
### 🗨️ Slides 

## Streamlit Pages

- **[BioGen](BioGen.py)** – generate concise bios by combining content scraping
  and semantic search.
- **[RAG](pages/2_RAG.py)** – search your database or uploaded documents with
  retrieval-augmented generation.
- **[Outreach](pages/3_Outreach.py)** – craft personalised email templates using
  AI assistance.
- **[Desktop Research](pages/4_Desktop_Research.py)** – perform deeper
  internet or local file searches.
- **[PDF Extractor](pages/5_PDF_Extractor.py)** – extract text from uploaded PDF
  documents.
- **[Deep Research](pages/6_Deep_Research.py)** – gather extended background
  information on selected delegates.

### Backend Modules
- **[Content Scraping](con_research/src/modules/scrapping_module.py)** – extract
  text from HTML pages or PDF documents.
- **[Semantic Search](con_research/src/modules/search_module.py)** – perform
  semantic queries using external search APIs.

## Fact Checking
To maintain credibility the app verifies scraped data where possible and allows
users to report inaccuracies. Data sources are cited so information can be
cross-checked.

## Limitations & Areas for Improvement
The current implementation provides useful tools but has several limitations.

### Limitations

**Static Web Scraping** – dynamic content may be missed when pages rely heavily
on JavaScript.

**Limited Data Sources** – results depend on the public web and may be
incomplete or outdated.

**No Contextual Understanding** – bios are generated from scraped content and
may lack nuance.

### Possible Improvements
*Expand data sources* to include academic databases and professional networks.
*Collect user feedback* to iteratively improve results.
*Add robust error handling and logging* for easier troubleshooting.

## UI


### 💻 StreamLit
![](https://github.com/natnew/Conference-Research/blob/main/con_research/data/Screenshot%202024-05-23%20223140.png)


### 🖱️ Others

## 💻 Setup
1. Install Python 3.10 or newer and create a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   xargs -a packages.txt sudo apt-get install -y  # optional
   ```
3. Copy your API keys to `.streamlit/secrets.toml` and update `config.yaml` as
   needed.
4. Launch the app:
   ```bash
   streamlit run BioGen.py
   ```

See [docs/INSTALLATION.md](docs/INSTALLATION.md) for more details.

## Usage
1. Start the Streamlit server as shown above.
2. Navigate through the pages using the left sidebar.
3. Upload conference lists or search the internet to build delegate profiles.
4. Filter and query the database from the **RAG** page.
5. Compose outreach emails directly within the **Outreach** page.

Additional scenarios are available in
[docs/USAGE_EXAMPLES.md](docs/USAGE_EXAMPLES.md).

## Documentation
- [User Guide](reports/User_Guide.md)
- [FAQ](reports/FAQ.md)
- [Installation Guide](docs/INSTALLATION.md)
- [Architecture Overview](docs/Architecture.md)
- [Contributing Guide](Contributing.md)
- [Code of Conduct](CodeOfConduct.md)
- [Changelog](CHANGELOG.md)

## License
This project is licensed under the [MIT License](LICENSE).
