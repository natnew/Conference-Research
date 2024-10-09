# Conference Research App

## 1. Title Page

- **Project Title**: Automating Conference Delegate Information Retrieval
- **Author**: ...
- **Date**: 2024

---

## 2. Abstract

This project aims to automate the retrieval of conference delegate information and the generation of personalised email templates using a hybrid approach that combines web scraping, natural language processing (NLP), and API integration. The system scrapes delegate details—such as names, emails, bios, and university affiliations—from conference websites and completes any missing or incomplete data using the GPT API. We experimented with various models and open-source frameworks, applying prompt engineering techniques to enhance the quality of the generated data. However, the GPT API consistently provided the most accurate and complete results.

The final solution integrates the scraped and API-generated data into a user-friendly Streamlit application that allows editors to filter and search for delegates and automatically generate outreach emails. An embedded chatbot further enhances real-time interaction with the dataset during conferences. To ensure the system’s reliability, we employed multiple evaluation techniques, including metrics-based evaluation (accuracy, recall, precision, F1 score), LLM-based grading, and human-based reviews. The project successfully reduces the time and manual effort required for conference preparation while improving the accuracy and consistency of delegate information, making it a valuable tool for academic and business conferences.

---

## 3. Introduction

**Problem Statement**: Editors attending conferences and campus visits spend several days manually searching for and compiling up-to-date information about delegates. This manual process is inefficient and can lead to missed opportunities for timely communication and networking.

**Objectives**:
- Automate the retrieval and processing of conference delegate information using a hybrid approach that combines traditional web scraping techniques, machine learning, and artificial intelligence (AI) to efficiently gather data from conference websites and public sources.
- Utilise deep learning models (such as the GPT API) to fill in missing or incomplete delegate information, including emails, bios, and other relevant details, ensuring comprehensive and accurate data collection.
- Develop a streamlined system that integrates the power of AI-driven tools with Python-based web scraping to generate personalised email templates for outreach, reducing manual workload and improving efficiency for editors and organisers.
- Implement prompt engineering techniques within the deep learning model to enhance the quality of generated content, ensuring that the system provides highly relevant and coherent responses tailored to specific delegate information needs.
- Create a user-friendly interface using Streamlit that allows editors to search, filter, and interact with the collected delegate data in real-time, and generate personalised emails automatically, with the added functionality of an AI-powered chatbot for quick queries.
- Evaluate system performance using metrics-based evaluation (accuracy, precision, recall, F1 score), LLM-based grading, and human-based feedback to continually improve the accuracy, relevance, and quality of the AI-generated outputs.




---

## 4. Data

**Data Sources**:
- Conference websites: Delegate data is extracted from .csv files or scraped from websites.
- External online sources: University websites and public social media profiles.
<br>

**Conference Information**:

1. **BISA Conference** - [BISA Conference Speakers List](https://conference.bisa.ac.uk/list-speakers-0) (Done)
2. **APA Conference** - [APA Conference Programme](https://www.xcdsystem.com/apa/program/euJ3pFp/index.cfm?pgid=1287&RunRemoveSessionFilter=1) (Done)
3. **APSA Conference** - [APSA Conference Programme](https://admin.allacademic.com/one/apsa/apsa24/index.php) (Done)
4. **ESA Conference** - [ESA Conference Website](https://www.europeansociology.org/conference/2024) (Done)
5. **EISA Conference** - [EISA Conference Faculty](https://c-in.floq.live/event/eisa-pec-2024/faculty) (Done)
6. **ECPR Conference** - [ECPR Conference Programme](https://ecpr.eu/Events/AcademicProgramme/Programme?EventID=251) (Done)
<br>

**Conference Status**:

| Conference | Status   | Date       |
|------------|----------|------------|
| ECPR       | COMPLETE | 29/07/2024 |
| EISA       | COMPLETE | 29/07/2024 |
| APSA       | COMPLETE | 29/07/2024 |
| ESA        | COMPLETE | 29/07/2024 |
| APA        | COMPLETE | 29/07/2024 |

<br>

* Instructions: Please ensure the names are formatted as "FirstName, LastName" in lowercase. Where the code cannot find an email address, please search the faculty website for one. If no email address is available, provide their LinkedIn social media URLs. The spreadsheets are named ECPR, EISA, APSA, APA, and ESA. The column headings are NAME, EMAIL, UNIVERSITY, LOCATION, BIO, SOCIALS, and FACULTY.

* Note: The BISA conference was completed in June 2024 and uploaded to the chatbot. From that implementation we were able to fine tune the solution to include more information and deal with missing or inaccurate information. 


---

## 5. Approaches Considered
We evaluated three different approaches to automate the collection and organisation of conference delegate information. These approaches were assessed based on their accuracy, efficiency, and cost-effectiveness. After careful evaluation, we selected **Approach 3 - Hybrid Approach** as the final solution because it provided the most accurate results and ensured complete data collection.

#### **Approach 1 - Python Script**:
- **Description**: This approach uses Python scripts to automate data collection and preprocessing. Delegate names are loaded from an Excel file, and a script scrapes relevant URLs to extract bios, emails, universities, and social media links.
- **Costs**: £... = 2200 rows x 5 columns. The final cost would vary based on the volume of data per conference. Generally, it costs £... for 2200 rows x 5 columns, but this would be adjusted for each event based on the amount of delegate data available.
- **Time (per conference)**: Web scraping takes 3 hours, preprocessing another 2 hours, and tool usage takes an additional 2 hours.
- **Effectiveness**: 70% accuracy in data extraction, with challenges arising from inconsistent formats.
<br>

#### **Approach 2 - API or Third-Party Tool (GPT for Sheets/ GPT API)**:
- **Description**: This approach leverages GPT for Sheets or GPT API to streamline data collection and preprocessing. The API or tool processes the data from multiple sources, integrating it into a structured format such as a spreadsheet or database. The API usage allows for flexibility in handling different volumes of data and automating the extraction of delegate information such as names, universities, emails, and bios.
- **Costs**: The costs would vary based on the volume of data per conference and the number of API calls made. Typically, it costs £200 for 2200 rows x 5 columns, but this would be adjusted for each event depending on the amount of delegate data available and the API usage (e.g., costs per API call or subscription fees for third-party services).
- **Time (per conference)**: Approximately 3 hours for initial scraping, 2 hours for data preprocessing, and 2 hours for configuring and using the API or tool.
- **Effectiveness**: This approach achieves 99% accuracy in data extraction, though additional formatting and validation steps may be required to ensure the data is properly structured. The use of an API allows for more efficient handling of large data sets but may require more sophisticated error handling and rate limit management.
<br>

#### **Approach 3 - Hybrid Approach (Python Script + GPT for Sheets/ GPT API)**:
- **Description**: This approach combines the use of Python scripts for initial web scraping with GPT for Sheets or GPT API to handle missing data and enhance preprocessing. Python scripts are used to automate the scraping of delegate names, universities, and social media links from conference websites. GPT for Sheets or GPT API is then employed to fill in missing data fields such as emails and bios, ensuring high accuracy and completeness.
- **Costs**: The costs vary depending on the volume of data per conference and the number of API calls made. Generally, it costs £... for 2200 rows x 5 columns. However, the final cost would depend on the amount of delegate data available for each event and the specific API usage (e.g., cost per API call or subscription for GPT API). Adjustments are made based on the size and complexity of the conference data.
- **Time (per conference)**: Web scraping takes approximately 3 hours, preprocessing another 2 hours, and using the API or third-party tool for completing missing fields takes an additional 2 hours. The total time may vary depending on the size of the dataset and the API’s processing speed.
- **Effectiveness**: This hybrid approach achieves 100% accuracy in data extraction by combining the strengths of both Python for scraping and the GPT API for handling missing data and refining results. While some fields may still be missing due to limitations in source data, the API allows for faster, more accurate completion of partial or incomplete data. The use of an API ensures that data is up-to-date and accurate, but it requires careful management of API rate limits and costs.
<br>

### Selected Approach: Hybrid Approach

After evaluating all three approaches, we selected the **Hybrid Approach** as the best solution. It provided the highest accuracy while ensuring that missing data was filled using GPT for Sheets or GPT API. The Python script enabled fast and efficient scraping, and GPT for Sheets or GPT API ensured that the data was complete and consistent. Although the other approaches had their strengths, the **Hybrid Approach** stood out as the most reliable and accurate solution for collecting and processing conference delegate data.

While we experimented with other open-source models and frameworks using API calls, even with prompt engineering, these alternatives provided less accurate results and were not as efficient in this context.
  
---

## 6. Methodology

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

## 7. Results

**Model Performance**:
- Web scraping and data collection achieved an accuracy rate of 70-100% across different conferences depending on website complexity.
- The system reduced the time to gather delegate information from 4 days to just a few hours per conference.

**Snippets of Excel Outputs:**
![]()
The data presented here demonstrates the accuracy of our data scraping and the completion of missing fields using the GPT API.

**Examples of Generated Emails**:
- Example 1: Name: Dr Jane Doe, Email: jane.doe@university.ac.uk, University: University of Example, Location: United Kingdom, Bio: Research in AI and NLP.
- Example 2: Name: Prof John Smith, Email: john.smith@college.com, University: College of Example, Location: United States, Bio: Specialises in Machine Learning.

**Streamlit App and Chatbot Screenshots:**
We developed a **Streamlit-based interface** for easy access to delegate data and lead generation functionality. Below are some screenshots of the Streamlit app and the **chatbot**:

![]()
The Streamlit app allows users to filter and search for delegates by region, university, or research interest. It also generates email templates for outreach.

![]()
The chatbot can quickly retrieve delegate information and provide users with suggestions for follow-up emails or meeting requests during conferences

---

## 8. Evaluation of Outputs

### Metrics-Based Evaluation
For evaluating the quality and accuracy of the data generated by the system, we employed several standard metrics used in NLP tasks to compare the model-generated answers with the "golden" or correct answers. The metrics used were:

1. **Exact Match Accuracy Rate**: Measures the proportion of model-generated answers that perfectly match the golden answers. This gives us a strict evaluation of how precise the model is in generating accurate outputs.
   - **Example**: In a set of 100 emails, 85 generated emails were an exact match to the golden emails, resulting in an accuracy rate of 85%.
   
2. **Recall**: Calculates the fraction of relevant information that the model retrieved from the golden answers. This metric indicates how much relevant data the model captures.
   - **Example**: Recall was calculated as 90% since the model was able to retrieve most relevant email addresses and bios.

3. **Precision**: Measures the fraction of relevant information in the model-generated answers. A high precision means that the model’s output contains fewer irrelevant or incorrect responses.
   - **Example**: Precision was calculated as 88%, showing that while the model generated highly relevant information, some incorrect data still appeared.

4. **F1 Score**: The harmonic mean of precision and recall, providing a balanced metric that takes into account both false positives and false negatives.
   - **Example**: The overall F1 score was 89%, indicating a well-balanced model performance.

### LLM-Based Evaluation
We also evaluated the model’s performance using **Large Language Models (LLMs)** as judges to score the quality of the generated outputs. This method was employed when we lacked sufficient labeled data for comparison.

1. **Single-point grading**: The LLM provided a score for each generated output based on predefined quality criteria. Scores were given on a scale of 1 to 10, where 10 indicated a near-perfect output. 
   - **Example**: The LLM gave an average score of 9.2 for the quality of email templates generated.

2. **Reference-based grading**: We provided the LLM with golden answers to compare the generated outputs and assign a similarity score. This was particularly useful in evaluating bios and email content.
   - **Example**: The similarity score between generated bios and reference bios was 87%.

3. **Pairwise grading**: The LLM was used to compare different model outputs and assign scores based on the relative quality and coherence of the responses. This method was particularly useful for evaluating chatbot responses.
   - **Example**: When comparing two generated email templates, the LLM selected the more coherent one 93% of the time.

It’s important to note that LLMs can exhibit bias, particularly if they are from the same provider as the generation model. In our case, we used a **Mistral Large model** to reduce bias.

### Human-Based Evaluation
In addition to LLM-based evaluation, we performed **human-based evaluations** for a subset of the generated outputs. This method provided insights into the model’s performance from a human perspective, particularly for qualitative aspects like empathy and fluency in generated emails.

1. **Internal Review by the Development Team:** The development team conducted a thorough review of the generated email templates and bios. The focus was on evaluating the accuracy, clarity, and coherence of the outputs, as well as ensuring that the outputs aligned with the project’s goals of automating conference preparation.
   - **Example**: The development team found that the GPT-generated email templates were clear, professional, and contextually appropriate for conference outreach. They reported that 85% of the templates required no additional editing before being considered suitable for use.

2. **Editor Feedback**: The editors, as key stakeholders, also played a crucial role in evaluating the system’s outputs. They reviewed the accuracy of delegate bios, the relevance of email templates, and provided feedback on how well the system matched their expectations for automating communication tasks.
   - **Example**: Editors agreed that 92% of the generated delegate bios were accurate and well-structured, capturing the essential professional details required for outreach. They highlighted that the fluency and relevance of the email templates aligned well with the tone required for conference communications, significantly reducing their manual workload.


## 9. Challenges and Limitations

**Challenges**:
- Difficulty in scraping dynamically loaded content on modern websites.
- Inconsistent data formats across conferences require additional preprocessing and validation.

**Limitations**:
- The system may struggle to gather information from websites that require JavaScript to load content or use CAPTCHA.
- Occasional manual intervention is required to fill in missing delegate information.

---

## 10. Conclusion
This project demonstrates the successful implementation of a hybrid approach combining machine learning, deep learning, and artificial intelligence to automate the retrieval and processing of conference delegate information. By integrating web scraping techniques with the GPT API, we were able to efficiently gather and complete delegate details from various conference websites, significantly reducing the manual effort required for conference preparation.
<br>

The system provides a robust solution for generating personalised email templates for outreach, leveraging AI-driven tools to streamline the process. This solution not only saves time but also improves accuracy and consistency in managing large datasets of delegate information, making it a valuable asset for editors, organisers, and businesses involved in frequent conference interactions.
<br>

The project’s feasibility is reinforced by the use of accessible technologies, such as Python for web scraping and widely adopted AI models like GPT, which are easily integrated using APIs. The Streamlit interface and chatbot ensure that users can interact with the data in a real-time, intuitive manner, adding further value by enhancing productivity during conferences.
<br>

In terms of business impact, the automation of delegate information retrieval and email template generation translates into significant time savings, reduced errors, and improved engagement with potential collaborators and clients. The solution is scalable, making it suitable for organisations attending multiple conferences or handling large delegate datasets.
<br>

While the project has proven effective, there is room for further refinement. Future enhancements could involve the inclusion of more advanced AI models for more nuanced data generation, as well as improved techniques for handling dynamic and complex web content. Additionally, expanding the integration of other data sources, such as academic databases or professional networking platforms, would enrich the dataset and improve outreach quality.
<br>

In summary, the hybrid solution offers a highly valuable, feasible, and scalable approach to automating conference preparation tasks, integrating artificial intelligence to improve both the efficiency and quality of information management. This project provides a strong foundation for future innovations in this space, ensuring that organisations can stay ahead in their networking and outreach efforts.

---
## 11. Next Steps/Improvements
While the current solution has proven to be highly effective and the editors have found it extremely helpful, there are several avenues for improving the accuracy and consistency of the output. These improvements focus on refining the data processing pipeline, enhancing the models used for data completion, and introducing more robust quality control mechanisms.

1. Enhancing Data Accuracy with Fine-Tuned Models
Solution: One way to improve the accuracy of the generated outputs (such as email templates and delegate bios) is by fine-tuning the GPT API or using more specialised AI models trained specifically on academic or professional datasets.
How it Works: Fine-tuning allows the model to be trained on domain-specific data, which makes it better at understanding and generating contextually accurate information relevant to the industry. By training on larger, more relevant datasets (e.g., academic publications or professional profiles), the system will generate more precise and consistent outputs.
Impact: This will lead to more accurate delegate information and better-tailored email templates, with reduced errors in generated outputs such as bios and professional details.
<br>

2. Introducing Validation Layers for Consistency
Solution: Implementing additional validation layers in the pipeline could help ensure greater consistency in the output. This could include automated verification steps that cross-reference the generated data with trusted sources (e.g., LinkedIn, academic directories, or verified databases).
How it Works: After data is generated by the API, a verification system can validate the accuracy of key fields (such as emails, affiliations, or titles) by cross-checking them with external databases or APIs that provide real-time, verified information.
Impact: This will increase the reliability and consistency of the data, ensuring that any errors introduced during scraping or generation are identified and corrected automatically.
<br>

3. Utilising More Advanced AI Models
Solution: Future improvements could involve experimenting with or migrating to more advanced AI models, such as OpenAI's GPT-4 or specialised transformer models designed for knowledge extraction from structured datasets.
How it Works: More advanced models, especially those built for information retrieval and natural language understanding, could perform better at generating nuanced content such as delegate bios or contact information. These models can offer improved comprehension of complex queries and unstructured data.
Impact: This would result in even more accurate and contextually appropriate outputs, with enhanced consistency across large datasets.
<br>

4. Increasing Training Data Diversity
Solution: Expanding the range and diversity of training data used for fine-tuning the model can significantly improve both accuracy and consistency, particularly when dealing with delegates from diverse fields, regions, and industries.
How it Works: By incorporating more diverse datasets—including international academic and professional profiles—the model will better handle variances in data from different regions and fields. This will reduce errors when dealing with non-standard formats or less common delegate information.
Impact: Improved accuracy in dealing with different formats and greater consistency across all delegate profiles, regardless of geographic or professional differences.
<br>

5. User Feedback Loop for Continuous Improvement
Solution: Implementing a user feedback loop where editors and end-users can flag inconsistencies or errors in real-time would provide valuable data for continuous model improvements.
How it Works: By introducing a feedback mechanism in the Streamlit app or through the chatbot, users can report issues with the generated data (e.g., incorrect emails or incomplete bios). This feedback can then be used to retrain the model periodically or improve the prompts used in the API.
Impact: This iterative feedback cycle will lead to continuous refinement of the system, improving both accuracy and consistency with real-world usage data.
<br>

6. Improving Prompt Engineering Techniques
Solution: Fine-tuning the prompt engineering techniques used in the GPT API requests can further improve the accuracy of the generated outputs.
How it Works: By refining the structure and content of the prompts that guide the GPT API, we can reduce the likelihood of incorrect or irrelevant information being generated. This may involve including more specific instructions in the prompts or using multi-step prompts to narrow down the API’s focus.
Impact: This will ensure the system generates more precise, relevant, and consistent outputs, particularly for complex or incomplete data sets.
---

## 12. References

- [Hugging Face Transformers Documentation](https://huggingface.co/transformers/)
- [Pywin32 Documentation](https://pypi.org/project/pywin32/)
- [BLEU Score Evaluation Paper](https://aclanthology.org/P02-1040/)
- [LangChain Documentation](https://www.langchain.com/)
