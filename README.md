# Conference Research
Conduct your own conference research in a few simple steps!

This is the repo to build a conference research app.

+------------------------------------------+
|         User Interface (Streamlit)       |
|------------------------------------------|
|  - User uploads Excel file               |
|  - User clicks "Generate Bios" button    |
|  - User searches for name in database    |
|  - User drafts lead generation email     |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|         File Handling Module             |
|------------------------------------------|
|  - Reads uploaded Excel file             |
|  - Displays uploaded DataFrame           |
|  - Sends names to Web Scraping Module    |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|         Web Scraping Module              |
|------------------------------------------|
|  - Uses SerperDevTool for search         |
|  - Uses ContentScraper for scraping      |
|  - Aggregates scraped content            |
|  - Sends content to Bio Generation       |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|         Bio Generation Module            |
|------------------------------------------|
|  - Uses OpenAI API to generate bios      |
|  - Receives and updates DataFrame        |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|         Database Integration Module      |
|------------------------------------------|
|  - Stores updated DataFrame in database  |
|  - Periodically updates bios             |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|         Search Module                    |
|------------------------------------------|
|  - User inputs name to search            |
|  - Queries database for name             |
|  - Retrieves and displays info           |
+-------------------+----------------------+
                    |
                    v
+------------------------------------------+
|         Lead Generation Email Module     |
|------------------------------------------|
|  - Provides email drafting template      |
|  - Allows personalization with info      |
+------------------------------------------+



# UI


### StreamLit


### Others

# Setup
- install the requirements from requirements.txt

- rename .streamlit/_secrets.toml to .streamlit/secrets.toml and place your secrets there

>streamlit run BioGen.py
