# Conference Research
📶 Conduct your own conference research in a few simple steps!

This is the repo to build a conference research app.

## Project
💡 This project is a Streamlit-based application that automates the generation of biographical content and assists in lead generation through a series of interconnected modules.

- User provides a PDF or URL with conference attendees' names.
- Agents scrape the internet for participant bios and store them in a database.
- User filters names by geographic region or university and selects participants based on bios.
- User uses AI-powered email generation template to craft lead generation emails; the app refreshes 5 times a year for each conference and supports multiple users.

## Presentation
### 📹 Video 
### 🗨️ Slides 

## AI System Description

- [Content Scraping](https://github.com/natnew/Conference-Research/blob/main/con_research/src/modules/scrapping_module.py): provides functionality to extract text from both HTML web pages and PDF documents by identifying the content type and applying appropriate scraping methods.
- [Semantic Search Queries](https://github.com/natnew/Conference-Research/blob/main/con_research/src/modules/search_module.py): implements a tool to perform semantic searches using a search API, sending queries and processing the responses to retrieve relevant URLs.
- [Streamlit Interface for Bio Generation](https://github.com/natnew/Conference-Research/blob/main/BioGen.py) sets up a Streamlit application to generate concise bios for conference participants by integrating content scraping and semantic search functionalities.
- [Search for Information in Database](https://github.com/natnew/Conference-Research/blob/main/pages/2_RAG.py) section provides functionality to query and retrieve specific information from a database, aiding users in accessing relevant data efficiently.
- [Update Database Using Agents]() section outlines how autonomous agents can be used to update a database with new or revised information.
- [Craft Email Templates Using AI](https://github.com/natnew/Conference-Research/blob/main/pages/3_LeadGen.py) section demonstrates the use of AI to generate personalized email templates for conference attendees.


## Limitations & Areas for Improvement
🩺 The current implementation of the project provides valuable tools for conference attendees to prepare for networking, but there are several limitations and areas for improvement to enhance its effectiveness and reliability.

### Limitations

**Static Web Scraping:**
- The current content scraping approach relies on static HTML and PDF scraping, which might not handle dynamic content effectively. Many modern websites load content dynamically using JavaScript, and the static scraping methods might miss critical information.

**Limited Data Sources:**
- The semantic search tool uses a specific search API and relies heavily on the content available on the web. This approach might not always retrieve comprehensive or accurate information, especially for websites that have not been updated with the most relevant information or who do not provide biographical information.

**No Contextual Understanding:**
- The bio generation process does not include advanced contextual understanding. It relies solely on the scraped content, which might lead to inaccuracies or incomplete bios if the content is not well-structured or detailed.

### Possible Improvements
**Expanding Data Sources:**
- Incorporate additional data sources such as academic databases, professional networking sites, and other authoritative sources to improve the comprehensiveness and reliability of the retrieved information.

**User Feedback and Iterative Improvement:**
- Incorporate user feedback mechanisms to continuously improve the system. Implement a way for users to report inaccuracies or suggest enhancements, allowing for iterative improvements based on real-world usage.

**Robust Error Handling and Logging:**
- Implement more robust error handling mechanisms to cover a wider range of potential issues. Incorporate logging to track errors and performance metrics, which can help in diagnosing and resolving issues more efficiently.

## UI


### 💻 StreamLit


### 🖱️ Others

## 💻 Setup
- install the requirements from requirements.txt

- rename .streamlit/_secrets.toml to .streamlit/secrets.toml and place your secrets there

>streamlit run BioGen.py
