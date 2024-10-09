# Conference Research App

## 1. Title Page

- **Project Title**: Automating Conference Delegate Information Retrieval
- **Author**: [Your Name]
- **Date**: [Project Date]

---

## 2. Abstract

This project aims to automate email template generation using Natural Language Processing (NLP). By training a model on sample email data, the system generates personalized email templates. The project explores data preprocessing, model training, and integration with Microsoft Outlook to automatically generate and send emails.

---

## 3. Introduction

**Problem Statement**: Editors attending conferences and campus visits spend several days manually searching for and compiling up-to-date information about delegates. This manual process is inefficient and can lead to missed opportunities for timely communication and networking.

**Objectives**:
- Automate delegate information retrieval from conference websites and external data sources.
- Develop a machine learning-based system capable of scraping, organising, and generating relevant delegate information.
- Provide editors with a user-friendly interface to access and update delegate profiles.
- Generate personalised email templates for lead generation and outreach.


---

## 4. Data

**Data Sources**:
- Conference websites: Delegate data is extracted from .csv files or scraped from websites.
- External online sources: University websites and public social media profiles.

**Data Preprocessing**:
- Web scraping using libraries like BeautifulSoup and Selenium to gather delegate names, emails, university affiliations, locations, bios, and social media links.
- Data cleaning and validation to ensure the accuracy and completeness of the information.
- Handling missing fields by searching for alternative sources, such as university pages and social media profiles.

---

## 5. Methodology

**Tools and Libraries**:
- Python: Pandas, BeautifulSoup, Selenium, GPT for Sheets, CrewAI, Pdfminer, LangChain.
- Model: Named Entity Recognition (NER) models for extracting key information such as names, affiliations, and research interests.
- Scraping Tools: SerpAPI, GPT for Sheets for filling missing data.
- Integration: Development of a user-friendly interface for editors, allowing seamless access to and updating of delegate profiles.

**Data Collection:**
- Delegate names and universities are scraped from conference websites.
- Additional delegate information is gathered by searching for university homepages and social media links.

**Model Training**:
- Machine learning models, including large language models (LLMs), are trained to automate the retrieval of delegate information and organisation into structured data.
- NLP tools are used to generate personalised email templates based on delegate information.

**Evaluation**:
- Accuracy of data extraction was evaluated through manual review and automated testing for missing or incomplete fields.
- Efficiency was measured by the reduction in time taken to retrieve delegate information compared to manual processes.

---

## 6. Results

**Model Performance**:
- Web scraping and data collection achieved an accuracy rate of 70-100% across different conferences depending on website complexity.
- The system reduced the time to gather delegate information from 4 days to just a few hours per conference.

**Examples of Generated Emails**:
- Example 1: Name: Dr Jane Doe, Email: jane.doe@university.ac.uk, University: University of Example, Location: United Kingdom, Bio: Research in AI and NLP.
- Example 2: Name: Prof John Smith, Email: john.smith@college.com, University: College of Example, Location: United States, Bio: Specialises in Machine Learning.

---

## 7. Challenges and Limitations

**Challenges**:
- Difficulty in scraping dynamically loaded content on modern websites.
- Inconsistent data formats across conferences require additional preprocessing and validation.

**Limitations**:
- The system may struggle to gather information from websites that require JavaScript to load content or use CAPTCHA.
- Occasional manual intervention is required to fill in missing delegate information.

---

## 8. Conclusion

...

---

## 9. References

- [Hugging Face Transformers Documentation](https://huggingface.co/transformers/)
- [Pywin32 Documentation](https://pypi.org/project/pywin32/)
- [BLEU Score Evaluation Paper](https://aclanthology.org/P02-1040/)
- [LangChain Documentation](https://www.langchain.com/)
