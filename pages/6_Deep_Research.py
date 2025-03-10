# import streamlit as st
# import time
# import os
# import logging
# from typing import List, Dict, TypedDict, Literal, Annotated, Union
# from pydantic import BaseModel, Field
# from openai import OpenAI
# from brave import Brave
# from openai import LengthFinishReasonError
# import operator

# # Set up logging configuration
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
# logger = logging.getLogger(__name__)
# openai_api_key = st.secrets["openai_api_key"]
# # Initialize OpenAI client
# client = OpenAI(api_key=openai_api_key)
# model = "gpt-4o-mini"

# # Initialize Brave client
# brave_api_key = st.secrets["brave_api_key"]
# brave = Brave(api_key=brave_api_key)

# # --------------------------------------------------------------
# # Step 1: Define the data models
# # --------------------------------------------------------------

# class Section(BaseModel):
#     name: str = Field(description="Section name")
#     description: str = Field(description="Overview of section topics")
#     research: bool = Field(description="Research required flag")
#     content: str = Field(description="Section content")

# class Sections(BaseModel):
#     sections: List[Section] = Field(description="Sections of the report.")

# class SearchQuery(BaseModel):
#     search_query: str = Field(None, description="Query for web search.")

# class Queries(BaseModel):
#     queries: List[SearchQuery] = Field(description="List of search queries.")

# class Feedback(BaseModel):
#     grade: Literal["pass", "fail"] = Field(description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail').")
#     follow_up_queries: List[SearchQuery] = Field(description="List of follow-up search queries.")

# class ReportStateInput(TypedDict):
#     topic: str  # Report topic

# class ReportStateOutput(TypedDict):
#     final_report: str  # Final report

# class ReportState(TypedDict):
#     topic: str  # Report topic
#     sections: List[Section]  # List of report sections
#     completed_sections: Annotated[List[Section], operator.add]  # Send() API key
#     report_sections_from_research: str  # String of any completed sections from research to write final sections
#     final_report: str  # Final report

# class SectionState(TypedDict):
#     section: Section  # Report section
#     search_iterations: int  # Number of search iterations done
#     search_queries: List[SearchQuery]  # List of search queries
#     source_str: str  # String of formatted source content from web search
#     feedback_on_report_plan: str  # Feedback on the report plan
#     report_sections_from_research: str  # String of any completed sections from research to write final sections
#     completed_sections: List[Section]  # Final key we duplicate in outer state for Send() API

# class SectionOutputState(TypedDict):
#     completed_sections: List[Section]  # Final key we duplicate in outer state for Send() API

# class SectionContent(BaseModel):
#     content: str = Field(description="Written content for the section")
#     key_points: List[str] = Field(description="Main points covered")

# # --------------------------------------------------------------
# # Step 2: Define prompts
# # --------------------------------------------------------------

# DEFAULT_REPORT_STRUCTURE = """The report structure should focus on breaking-down the user-provided topic:

# 1. Introduction (no research needed)
#    - Brief overview of the topic area

# 2. Main Body Sections:
#    - Each section should focus on a sub-topic of the user-provided topic
#    - Include any key concepts and definitions
#    - Provide real-world examples or case studies where applicable

# 3. Conclusion
#    - Aim for 1 structural element (either a list or table) that distills the main body sections
#    - Provide a concise summary of the report"""

# report_planner_query_writer_instructions = """You are an expert technical writer, helping to plan a report.

# <Report topic>
# {topic}
# </Report topic>

# <Report organization>
# {report_organization}
# </Report organization>

# <Task>
# Your goal is to generate {number_of_queries} search queries that will help gather comprehensive information for planning the report sections.

# The queries should:

# 1. Be related to the topic of the report
# 2. Help satisfy the requirements specified in the report organization

# Make the queries specific enough to find high-quality, relevant sources while covering the breadth needed for the report structure.
# </Task>"""

# report_planner_instructions = """I want a plan for a report.

# <Task>
# Generate a list of sections for the report.

# Each section should have the fields:

# - Name - Name for this section of the report.
# - Description - Brief overview of the main topics covered in this section.
# - Research - Whether to perform web research for this section of the report.
# - Content - The content of the section, which you will leave blank for now.

# For example, introduction and conclusion will not require research because they will distill information from other parts of the report.
# </Task>

# <Topic>
# The topic of the report is:
# {topic}
# </Topic>

# <Report organization>
# The report should follow this organization:
# {report_organization}
# </Report organization>

# <Context>
# Here is context to use to plan the sections of the report:
# {context}
# </Context>

# <Feedback>
# Here is feedback on the report structure from review (if any):
# {feedback}
# </Feedback>
# """

# query_writer_instructions = """You are an expert technical writer crafting targeted web search queries that will gather comprehensive information for writing a technical report section.

# <Section topic>
# {section_topic}
# </Section topic>

# <Task>
# When generating {number_of_queries} search queries, ensure they:
# 1. Cover different aspects of the topic (e.g., core features, real-world applications, technical architecture)
# 2. Include specific technical terms related to the topic
# 3. Target recent information by including year markers where relevant (e.g., "2024")
# 4. Look for comparisons or differentiators from similar technologies/approaches
# 5. Search for both official documentation and practical implementation examples

# Your queries should be:
# - Specific enough to avoid generic results
# - Technical enough to capture detailed implementation information
# - Diverse enough to cover all aspects of the section plan
# - Focused on authoritative sources (documentation, technical blogs, academic papers)
# </Task>"""

# section_writer_instructions = """You are an expert technical writer crafting one section of a technical report.

# <Section topic>
# {section_topic}
# </Section topic>

# <Existing section content (if populated)>
# {section_content}
# </Existing section content>

# <Source material>
# {context}
# </Source material>

# <Guidelines for writing>
# 1. If the existing section content is not populated, write a new section from scratch.
# 2. If the existing section content is populated, write a new section that synthesizes the existing section content with the new information.
# </Guidelines for writing>

# <Length and style>
# - Strict 150-200 word limit
# - No marketing language
# - Technical focus
# - Write in simple, clear language
# - Start with your most important insight in **bold**
# - Use short paragraphs (2-3 sentences max)
# - Use ## for section title (Markdown format)
# - Only use ONE structural element IF it helps clarify your point:
#   * Either a focused table comparing 2-3 key items (using Markdown table syntax)
#   * Or a short list (3-5 items) using proper Markdown list syntax:
#     - Use `*` or `-` for unordered lists
#     - Use `1.` for ordered lists
#     - Ensure proper indentation and spacing
# </Length and style>

# <Quality checks>
# - Exactly 150-200 words (excluding title and sources)
# - Careful use of only ONE structural element (table or list) and only if it helps clarify your point
# - One specific example / case study
# - Starts with bold insight
# - No preamble prior to creating the section content
# </Quality checks>
# """

# section_grader_instructions = """Review a report section relative to the specified topic:

# <section topic>
# {section_topic}
# </section topic>

# <section content>
# {section}
# </section content>

# <task>
# Evaluate whether the section adequately covers the topic by checking technical accuracy and depth.

# If the section fails any criteria, generate specific follow-up search queries to gather missing information.
# </task>

# <format>
#     grade: Literal["pass","fail"] = Field(
#         description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
#     )
#     follow_up_queries: List[SearchQuery] = Field(
#         description="List of follow-up search queries.",
#     )
# </format>
# """

# final_section_writer_instructions = """You are an expert technical writer crafting a section that synthesizes information from the rest of the report.

# <Section topic>
# {section_topic}
# </Section topic>

# <Available report content>
# {context}
# </Available report content>

# <Task>
# 1. Section-Specific Approach:

# For Introduction:
# - Use # for report title (Markdown format)
# - 50-100 word limit
# - Write in simple and clear language
# - Focus on the core motivation for the report in 1-2 paragraphs
# - Use a clear narrative arc to introduce the report
# - Include NO structural elements (no lists or tables)
# - No sources section needed

# For Conclusion/Summary:
# - Use ## for section title (Markdown format)
# - 100-150 word limit
# - For comparative reports:
#     * Must include a focused comparison table using Markdown table syntax
#     * Table should distill insights from the report
#     * Keep table entries clear and concise
# - For non-comparative reports:
#     * Only use ONE structural element IF it helps distill the points made in the report:
#     * Either a focused table comparing items present in the report (using Markdown table syntax)
#     * Or a short list using proper Markdown list syntax:
#       - Use `*` or `-` for unordered lists
#       - Use `1.` for ordered lists
#       - Ensure proper indentation and spacing
# - End with specific next steps or implications
# - No sources section needed

# 3. Writing Approach:
# - Use concrete details over general statements
# - Make every word count
# - Focus on your single most important point
# </Task>

# <Quality Checks>
# - For introduction: 50-100 word limit, # for report title, no structural elements, no sources section
# - For conclusion: 100-150 word limit, ## for section title, only ONE structural element at most, no sources section
# - Markdown format
# - Do not include word count or any preamble in your response
# </Quality checks>"""

# # --------------------------------------------------------------
# # Step 3: Implement the report generator
# # --------------------------------------------------------------

# class ReportGenerator:
#     def __init__(self):
#         self.sections_content = {}
#         self.sources = set()

#     def generate_search_queries(self, topic: str, report_organization: str, number_of_queries: int) -> List[SearchQuery]:
#         """Generate search queries for the report."""
#         system_instructions_query = report_planner_query_writer_instructions.format(
#             topic=topic, report_organization=report_organization, number_of_queries=number_of_queries
#         )
#         try:
#             completion = client.beta.chat.completions.parse(
#                 model=model,
#                 messages=[{"role": "system", "content": system_instructions_query}],
#                 response_format=Queries,
#             )
#             return completion.choices[0].message.parsed.queries
#         except LengthFinishReasonError as e:
#             st.error("Search query generation exceeded token limit. Returning truncated response.")
#             return e.completion.choices[0].message.parsed.queries  # Return the truncated queries

#     def generate_report_plan(self, topic: str, report_organization: str, context: str, feedback: str) -> Sections:
#         """Generate the report plan with sections."""
#         system_instructions_sections = report_planner_instructions.format(
#             topic=topic, report_organization=report_organization, context=context, feedback=feedback
#         )
#         try:
#             completion = client.beta.chat.completions.parse(
#                 model=model,
#                 messages=[{"role": "system", "content": system_instructions_sections}],
#                 response_format=Sections,
#             )
#             return completion.choices[0].message.parsed
#         except LengthFinishReasonError as e:
#             st.error("Report plan generation exceeded token limit. Returning truncated response.")
#             return e.completion.choices[0].message.parsed  # Return the truncated report plan

#     def write_section(self, section_topic: str, section_description: str, context: str, section_content: str) -> str:
#         """Write a section of the report."""
#         system_instructions = section_writer_instructions.format(
#             section_topic=section_topic, section_content=section_content, context=context
#         )
#         try:
#             completion = client.beta.chat.completions.parse(
#                 model=model,
#                 messages=[{"role": "system", "content": system_instructions}],
#                 response_format=SectionContent,
#             )
#             return completion.choices[0].message.parsed.content
#         except LengthFinishReasonError as e:
#             st.error("Section writing exceeded token limit. Returning truncated response.")
#             return e.completion.choices[0].message.parsed.content  # Return the truncated section content

#     def evaluate_section(self, section_topic: str, section_content: str) -> Feedback:
#         """Evaluate a section of the report."""
#         system_instructions = section_grader_instructions.format(section_topic=section_topic, section=section_content)
#         try:
#             completion = client.beta.chat.completions.parse(
#                 model=model,
#                 messages=[{"role": "system", "content": system_instructions}],
#                 response_format=Feedback,
#             )
#             return completion.choices[0].message.parsed
#         except LengthFinishReasonError as e:
#             st.error("Section evaluation exceeded token limit. Returning truncated response.")
#             return e.completion.choices[0].message.parsed  # Return the truncated feedback

#     def write_final_sections(self, section_topic: str, context: str) -> str:
#         """Write the final sections of the report."""
#         system_instructions = final_section_writer_instructions.format(section_topic=section_topic, context=context)
#         try:
#             completion = client.beta.chat.completions.parse(
#                 model=model,
#                 messages=[{"role": "system", "content": system_instructions}],
#                 response_format=SectionContent,
#             )
#             return completion.choices[0].message.parsed.content
#         except LengthFinishReasonError as e:
#             st.error("Final section writing exceeded token limit. Returning truncated response.")
#             return e.completion.choices[0].message.parsed.content  # Return the truncated final section content

#     def generate_report(self, topic: str, report_organization: str, context: str, feedback: str) -> ReportStateOutput:
#         """Generate the full report."""
#         progress_placeholder = st.empty()
#         progress_placeholder.info(f"Starting report generation for: {topic}")

#         # Generate search queries
#         search_queries = self.generate_search_queries(topic, report_organization, number_of_queries=2)
#         progress_placeholder.info(f"Generated search queries: {search_queries}")

#         # Perform web searches and collect sources
#         all_search_results = []
#         for query in search_queries:
#             search_results = web_search(query.search_query)
#             all_search_results.extend(search_results)

#         # Deduplicate and format sources
#         sources_list = deduplicate_and_format_sources(all_search_results, return_type="list")
#         self.sources.update(sources_list)

#         # Format sources for context
#         source_str = deduplicate_and_format_sources(all_search_results, return_type="string")

#         # Generate report plan
#         report_plan = self.generate_report_plan(topic, report_organization, source_str, feedback)
#         progress_placeholder.info(f"Generated report plan with {len(report_plan.sections)} sections")

#         # Write each section
#         for section in report_plan.sections:
#             progress_placeholder.info(f"Writing section: {section.name}")
#             section_content = self.write_section(section.name, section.description, source_str, section.content)
#             section.content = section_content
#             self.sections_content[section.name] = section

#         # Evaluate and refine sections
#         for section in report_plan.sections:
#             progress_placeholder.info(f"Evaluating section: {section.name}")
#             evaluation = self.evaluate_section(section.name, section.content)
#             if evaluation.grade == "fail":
#                 progress_placeholder.info(f"Section {section.name} failed evaluation. Generating follow-up queries.")
#                 follow_up_queries = evaluation.follow_up_queries
#                 # Perform follow-up searches and refine the section
#                 for query in follow_up_queries:
#                     search_results = web_search(query.search_query)
#                     all_search_results.extend(search_results)
#                 section_content = self.write_section(section.name, section.description, source_str, section.content)
#                 section.content = section_content
#                 self.sections_content[section.name] = section

#         # Write final sections
#         introduction = self.write_final_sections("Introduction", "\n\n".join([s.content for s in report_plan.sections]))
#         conclusion = self.write_final_sections("Conclusion", "\n\n".join([s.content for s in report_plan.sections]))

#         # Compile the final report
#         all_sections = "\n\n".join([s.content for s in report_plan.sections])
#         final_report = f"""
#         {introduction}

#         {all_sections}

#         {conclusion}
#         """

#         # Append sources to the final report
#         sources_section = deduplicate_and_format_sources(all_search_results, return_type="list")
#         sources_section_str = "\n".join(sources_section)
#         final_report += f"\n\n### Sources\n{sources_section_str}"

#         # Clear the progress placeholder
#         progress_placeholder.empty()

#         # Display "Research complete!" message
#         st.success("Research complete!")

#         return {"final_report": final_report}

# # --------------------------------------------------------------
# # Step 4: Define the tool for web search
# # --------------------------------------------------------------

# def web_search(query: str) -> List[Dict]:
#     """Perform a web search using Brave."""
#     try:
#         search_results = brave.search(q=query, count=3)
#         if search_results is None:
#             raise ValueError("Search results are None")
#         time.sleep(2) 
#         return search_results.web_results
#     except Exception as e:
#         return []


# def deduplicate_and_format_sources(search_response, return_type: str = "list") -> Union[str, List[str]]:
#     """
#     Takes a list of search responses and formats them into a readable string or list of sources.

#     Args:
#         search_response: List of search response dicts, each containing:
#             - title: str
#             - href: str
#             - body: str
#         return_type: str, either "list" or "string"

#     Returns:
#         Union[str, List[str]]: Formatted string with deduplicated sources or list of sources with title and URL
#     """
#     # Collect all results
#     sources_list = search_response

#     # Deduplicate by URL
#     unique_sources = {source['url']: source for source in sources_list}

#     if return_type == "list":
#         # Format output as a list of sources
#         formatted_sources = []
#         for source in unique_sources.values():
#             formatted_sources.append(f"- [{source['title']}]({source['url']})")
#         return formatted_sources
#     else:
#         # Format output as a string with context
#         formatted_text = ""
#         for i, source in enumerate(unique_sources.values(), 1):
#             formatted_text += f"- {source['title']}\n"
#             formatted_text += f"  URL: {source['url']}\n"
#             formatted_text += f"  Most relevant content from source: {source['description']}\n"
#         return formatted_text.strip()

# # --------------------------------------------------------------
# # Step 5: Streamlit app
# # --------------------------------------------------------------

# st.set_page_config(page_title="Deep Research", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")

# st.title("Deep Research")

# with st.sidebar:
#     st.title(":streamlit: Research Assistant")
#     st.write("A self-service app that automates the generation of reports and assists in research tasks.")

#     st.header("How It Works")
#     st.markdown(
#         """
# 1. Enter your research query below.
# 2. (Optional) Upload supplementary files (e.g., PDFs, images) for additional context.
# 3. Select your preferred **research engine** and **research depth**.
# 4. Click **Start Research** to begin the analysis.
# 5. Watch progress in real-time and review the final report with citations.
#         """
#     )

#     engine_choice = st.selectbox("Select Research Engine", options=["OpenAI"])
#     research_depth = st.selectbox("Select Research Depth", ["Basic", "In-depth", "Advanced"])

# st.markdown("### Enter Your Research Query")
# query = st.text_area("Type your query here...", height=150)

# uploaded_files = st.file_uploader("Upload supporting documents (optional)", type=["pdf", "png", "jpg"], accept_multiple_files=True)

# start_button = st.button("Start Research")

# report_placeholder = st.empty()

# if start_button:
#     if query.strip() == "":
#         st.warning("Please provide a query before starting the research.")
#     else:
#         with st.spinner("Deep Research in progress... This may take 5–30 minutes."):
#             # Initialize the report generator
#             report_generator = ReportGenerator()

#             # Generate the report
#             result = report_generator.generate_report(topic=query, report_organization=DEFAULT_REPORT_STRUCTURE, context="", feedback=None)

#             # Output the final report
#             final_report = result["final_report"]
#             report_placeholder.markdown(final_report, unsafe_allow_html=True)

# main.py - Main application file
import streamlit as st
import time
import logging
import json
from datetime import datetime
from typing import List, Dict, TypedDict, Literal, Annotated, Union, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
import functools
import operator
from pydantic import BaseModel, Field
from openai import OpenAI
from brave import Brave
from openai import LengthFinishReasonError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------
# Step 1: Define the data models
# --------------------------------------------------------------

class Section(BaseModel):
    name: str = Field(description="Section name")
    description: str = Field(description="Overview of section topics")
    research: bool = Field(description="Research required flag")
    content: str = Field(description="Section content")

class Sections(BaseModel):
    sections: List[Section] = Field(description="Sections of the report.")

class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Query for web search.")

class Queries(BaseModel):
    queries: List[SearchQuery] = Field(description="List of search queries.")

class Feedback(BaseModel):
    grade: Literal["pass", "fail"] = Field(description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail').")
    follow_up_queries: List[SearchQuery] = Field(description="List of follow-up search queries.")

class ReportStateInput(TypedDict):
    topic: str  # Report topic

class ReportStateOutput(TypedDict):
    final_report: str  # Final report

class ReportState(TypedDict):
    topic: str  # Report topic
    sections: List[Section]  # List of report sections
    completed_sections: Annotated[List[Section], operator.add]  # Send() API key
    report_sections_from_research: str  # String of any completed sections from research to write final sections
    final_report: str  # Final report

class SectionState(TypedDict):
    section: Section  # Report section
    search_iterations: int  # Number of search iterations done
    search_queries: List[SearchQuery]  # List of search queries
    source_str: str  # String of formatted source content from web search
    feedback_on_report_plan: str  # Feedback on the report plan
    report_sections_from_research: str  # String of any completed sections from research to write final sections
    completed_sections: List[Section]  # Final key we duplicate in outer state for Send() API

class SectionOutputState(TypedDict):
    completed_sections: List[Section]  # Final key we duplicate in outer state for Send() API

class SectionContent(BaseModel):
    content: str = Field(description="Written content for the section")
    key_points: List[str] = Field(description="Main points covered")

class SearchResult(BaseModel):
    title: str = Field(description="Title of the search result")
    url: str = Field(description="URL of the search result")
    description: str = Field(description="Description or excerpt from the search result")

# --------------------------------------------------------------
# Step 2: Define prompts in a separate module
# --------------------------------------------------------------

# prompts.py
class Prompts:
    """Collection of prompts used for report generation."""

    DEFAULT_REPORT_STRUCTURE = """The report structure should focus on breaking-down the user-provided topic:

    1. Introduction (no research needed)
       - Brief overview of the topic area

    2. Main Body Sections:
       - Each section should focus on a sub-topic of the user-provided topic
       - Include any key concepts and definitions
       - Provide real-world examples or case studies where applicable

    3. Conclusion
       - Aim for 1 structural element (either a list or table) that distills the main body sections
       - Provide a concise summary of the report"""

    @staticmethod
    def report_planner_query_writer(topic: str, report_organization: str, number_of_queries: int) -> str:
        return f"""You are an expert technical writer, helping to plan a report.

<Report topic>
{topic}
</Report topic>

<Report organization>
{report_organization}
</Report organization>

<Task>
Your goal is to generate {number_of_queries} search queries that will help gather comprehensive information for planning the report sections.

The queries should:

1. Be related to the topic of the report
2. Help satisfy the requirements specified in the report organization

Make the queries specific enough to find high-quality, relevant sources while covering the breadth needed for the report structure.
</Task>"""

    @staticmethod
    def report_planner(topic: str, report_organization: str, context: str, feedback: str) -> str:
        return f"""I want a plan for a report.

<Task>
Generate a list of sections for the report.

Each section should have the fields:

- Name - Name for this section of the report.
- Description - Brief overview of the main topics covered in this section.
- Research - Whether to perform web research for this section of the report.
- Content - The content of the section, which you will leave blank for now.

For example, introduction and conclusion will not require research because they will distill information from other parts of the report.
</Task>

<Topic>
The topic of the report is:
{topic}
</Topic>

<Report organization>
The report should follow this organization:
{report_organization}
</Report organization>

<Context>
Here is context to use to plan the sections of the report:
{context}
</Context>

<Feedback>
Here is feedback on the report structure from review (if any):
{feedback}
</Feedback>
"""

    @staticmethod
    def query_writer(section_topic: str, number_of_queries: int) -> str:
        return f"""You are an expert technical writer crafting targeted web search queries that will gather comprehensive information for writing a technical report section.

<Section topic>
{section_topic}
</Section topic>

<Task>
When generating {number_of_queries} search queries, ensure they:
1. Cover different aspects of the topic (e.g., core features, real-world applications, technical architecture)
2. Include specific technical terms related to the topic
3. Target recent information by including year markers where relevant (e.g., "2024")
4. Look for comparisons or differentiators from similar technologies/approaches
5. Search for both official documentation and practical implementation examples

Your queries should be:
- Specific enough to avoid generic results
- Technical enough to capture detailed implementation information
- Diverse enough to cover all aspects of the section plan
- Focused on authoritative sources (documentation, technical blogs, academic papers)
</Task>"""

    @staticmethod
    def section_writer(section_topic: str, section_content: str, context: str) -> str:
        return f"""You are an expert technical writer crafting one section of a technical report.

<Section topic>
{section_topic}
</Section topic>

<Existing section content (if populated)>
{section_content}
</Existing section content>

<Source material>
{context}
</Source material>

<Guidelines for writing>
1. If the existing section content is not populated, write a new section from scratch.
2. If the existing section content is populated, write a new section that synthesizes the existing section content with the new information.
</Guidelines for writing>

<Length and style>
- Strict 150-200 word limit
- No marketing language
- Technical focus
- Write in simple, clear language
- Start with your most important insight in **bold**
- Use short paragraphs (2-3 sentences max)
- Use ## for section title (Markdown format)
- Only use ONE structural element IF it helps clarify your point:
  * Either a focused table comparing 2-3 key items (using Markdown table syntax)
  * Or a short list (3-5 items) using proper Markdown list syntax:
    - Use `*` or `-` for unordered lists
    - Use `1.` for ordered lists
    - Ensure proper indentation and spacing
</Length and style>

<Quality checks>
- Exactly 150-200 words (excluding title and sources)
- Careful use of only ONE structural element (table or list) and only if it helps clarify your point
- One specific example / case study
- Starts with bold insight
- No preamble prior to creating the section content
</Quality checks>
"""

    @staticmethod
    def section_grader(section_topic: str, section: str) -> str:
        return f"""Review a report section relative to the specified topic:

<section topic>
{section_topic}
</section topic>

<section content>
{section}
</section content>

<task>
Evaluate whether the section adequately covers the topic by checking technical accuracy and depth.

If the section fails any criteria, generate specific follow-up search queries to gather missing information.
</task>

<format>
    grade: Literal["pass","fail"] = Field(
        description="Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail')."
    )
    follow_up_queries: List[SearchQuery] = Field(
        description="List of follow-up search queries.",
    )
</format>
"""

    @staticmethod
    def final_section_writer(section_topic: str, context: str) -> str:
        return f"""You are an expert technical writer crafting a section that synthesizes information from the rest of the report.

<Section topic>
{section_topic}
</Section topic>

<Available report content>
{context}
</Available report content>

<Task>
1. Section-Specific Approach:

For Introduction:
- Use # for report title (Markdown format)
- 50-100 word limit
- Write in simple and clear language
- Focus on the core motivation for the report in 1-2 paragraphs
- Use a clear narrative arc to introduce the report
- Include NO structural elements (no lists or tables)
- No sources section needed

For Conclusion/Summary:
- Use ## for section title (Markdown format)
- 100-150 word limit
- For comparative reports:
    * Must include a focused comparison table using Markdown table syntax
    * Table should distill insights from the report
    * Keep table entries clear and concise
- For non-comparative reports:
    * Only use ONE structural element IF it helps distill the points made in the report:
    * Either a focused table comparing items present in the report (using Markdown table syntax)
    * Or a short list using proper Markdown list syntax:
      - Use `*` or `-` for unordered lists
      - Use `1.` for ordered lists
      - Ensure proper indentation and spacing
- End with specific next steps or implications
- No sources section needed

3. Writing Approach:
- Use concrete details over general statements
- Make every word count
- Focus on your single most important point
</Task>

<Quality Checks>
- For introduction: 50-100 word limit, # for report title, no structural elements, no sources section
- For conclusion: 100-150 word limit, ## for section title, only ONE structural element at most, no sources section
- Markdown format
- Do not include word count or any preamble in your response
</Quality checks>"""

# --------------------------------------------------------------
# Step 3: API Client Classes
# --------------------------------------------------------------

# api_clients.py
class OpenAIClient:
    """Wrapper for OpenAI API with retry logic and error handling."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def parse_completion(
        self,
        system_prompt: str,
        response_format: BaseModel,
        temperature: float = 0.7
    ) -> Any:
        """Send a request to the OpenAI API with retry logic."""
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[{"role": "system", "content": system_prompt}],
                response_format=response_format,
                temperature=temperature
            )
            return completion.choices[0].message.parsed
        except LengthFinishReasonError as e:
            # Handle token limit issues
            logger.warning(f"Response truncated due to token limit: {e}")
            return e.completion.choices[0].message.parsed
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {e}")
            raise

class BraveClient:
    """Wrapper for Brave API with retry logic and error handling."""

    def __init__(self, api_key: str):
        self.brave = Brave(api_key=api_key)

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def search(self, query: str, count: int = 3) -> List[Dict]:
        """Perform a web search with retry logic."""
        try:
            search_results = self.brave.search(q=query, count=count)
            if search_results is None:
                raise ValueError("Search results are None")
            time.sleep(1)  # Reduced sleep time
            return search_results.web_results
        except Exception as e:
            logger.error(f"Error in Brave search: {e}")
            return []

# --------------------------------------------------------------
# Step 4: Utility Functions
# --------------------------------------------------------------

# utils.py
class ReportUtils:
    """Utility functions for report generation."""

    @staticmethod
    def deduplicate_and_format_sources(
        search_response: List[Dict],
        return_type: str = "list"
    ) -> Union[str, List[str]]:
        """Format search results into a readable string or list."""
        # Deduplicate by URL
        unique_sources = {source['url']: source for source in search_response}

        if return_type == "list":
            # Format output as a list of sources
            return [f"- [{source['title']}]({source['url']})" for source in unique_sources.values()]
        else:
            # Format output as a string with context
            formatted_text = ""
            for i, source in enumerate(unique_sources.values(), 1):
                formatted_text += f"- {source['title']}\n"
                formatted_text += f"  URL: {source['url']}\n"
                formatted_text += f"  Most relevant content from source: {source['description']}\n"
            return formatted_text.strip()

# --------------------------------------------------------------
# Step 5: Report Generator Class
# --------------------------------------------------------------

# report_generator.py
class ReportGenerator:
    """Main class for generating reports with research."""

    def __init__(self, openai_api_key: str, brave_api_key: str, model: str = "gpt-4o-mini"):
        self.openai_client = OpenAIClient(api_key=openai_api_key, model=model)
        self.brave_client = BraveClient(api_key=brave_api_key)
        self.sections_content = {}
        self.sources = set()
        self.prompts = Prompts()

    @st.cache_data(ttl=3600)  # Cache results for 1 hour
    def _cached_web_search(self, query: str, count: int = 3) -> List[Dict]:
        """Cached version of web search to avoid redundant API calls."""
        return self.brave_client.search(query=query, count=count)

    def _parallel_web_search(self, queries: List[SearchQuery], count: int = 3) -> List[Dict]:
        """Execute web searches in parallel."""
        all_results = []

        with ThreadPoolExecutor(max_workers=min(5, len(queries))) as executor:
            future_to_query = {
                executor.submit(self._cached_web_search, query.search_query, count): query.search_query
                for query in queries
            }

            for future in future_to_query:
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    logger.error(f"Error in parallel search: {e}")

        return all_results

    def generate_search_queries(
        self,
        topic: str,
        report_organization: str,
        number_of_queries: int = 2
    ) -> List[SearchQuery]:
        """Generate search queries for the report."""
        system_prompt = self.prompts.report_planner_query_writer(
            topic=topic,
            report_organization=report_organization,
            number_of_queries=number_of_queries
        )

        return self.openai_client.parse_completion(
            system_prompt=system_prompt,
            response_format=Queries
        ).queries

    def generate_report_plan(
        self,
        topic: str,
        report_organization: str,
        context: str,
        feedback: str
    ) -> Sections:
        """Generate the report plan with sections."""
        system_prompt = self.prompts.report_planner(
            topic=topic,
            report_organization=report_organization,
            context=context,
            feedback=feedback
        )

        return self.openai_client.parse_completion(
            system_prompt=system_prompt,
            response_format=Sections
        )

    def write_section(
        self,
        section_topic: str,
        section_description: str,
        context: str,
        section_content: str
    ) -> str:
        """Write a section of the report."""
        system_prompt = self.prompts.section_writer(
            section_topic=section_topic,
            section_content=section_content,
            context=context
        )

        return self.openai_client.parse_completion(
            system_prompt=system_prompt,
            response_format=SectionContent
        ).content

    def evaluate_section(self, section_topic: str, section_content: str) -> Feedback:
        """Evaluate a section of the report."""
        system_prompt = self.prompts.section_grader(
            section_topic=section_topic,
            section=section_content
        )

        return self.openai_client.parse_completion(
            system_prompt=system_prompt,
            response_format=Feedback
        )

    def write_final_sections(self, section_topic: str, context: str) -> str:
        """Write the final sections of the report."""
        system_prompt = self.prompts.final_section_writer(
            section_topic=section_topic,
            context=context
        )

        return self.openai_client.parse_completion(
            system_prompt=system_prompt,
            response_format=SectionContent
        ).content

    def generate_report(
        self,
        topic: str,
        report_organization: str,
        context: str = "",
        feedback: str = "",
        research_depth: str = "Basic"
    ) -> ReportStateOutput:
        """Generate the full report with progress tracking."""
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Determine search parameters based on research depth
            if research_depth == "Basic":
                query_count, search_count = 2, 3
            elif research_depth == "In-depth":
                query_count, search_count = 3, 5
            else:  # Advanced
                query_count, search_count = 4, 7

            # Step 1: Generate search queries (5%)
            status_text.info(f"Generating search queries for: {topic}")
            search_queries = self.generate_search_queries(
                topic=topic,
                report_organization=report_organization,
                number_of_queries=query_count
            )
            progress_bar.progress(5)

            # Step 2: Perform web searches (15%)
            status_text.info("Performing web searches")
            all_search_results = self._parallel_web_search(search_queries, count=search_count)
            progress_bar.progress(15)

            # Step 3: Format sources (20%)
            status_text.info("Processing search results")
            source_str = ReportUtils.deduplicate_and_format_sources(all_search_results, return_type="string")
            sources_list = ReportUtils.deduplicate_and_format_sources(all_search_results, return_type="list")
            self.sources.update(sources_list)
            progress_bar.progress(20)

            # Step 4: Generate report plan (30%)
            status_text.info("Creating report structure")
            report_plan = self.generate_report_plan(topic, report_organization, source_str, feedback)
            section_count = len(report_plan.sections)
            progress_bar.progress(30)

            # Step 5: Write each section (30% to 70%)
            section_progress_increment = 40 / section_count
            current_progress = 30

            for i, section in enumerate(report_plan.sections):
                status_text.info(f"Writing section {i+1}/{section_count}: {section.name}")
                section_content = self.write_section(
                    section.name,
                    section.description,
                    source_str,
                    section.content
                )
                section.content = section_content
                self.sections_content[section.name] = section

                current_progress += section_progress_increment
                progress_bar.progress(int(current_progress))

            # Step 6: Evaluate and refine sections (70% to 85%)
            section_eval_increment = 15 / section_count
            current_progress = 70

            for i, section in enumerate(report_plan.sections):
                status_text.info(f"Evaluating section {i+1}/{section_count}: {section.name}")
                evaluation = self.evaluate_section(section.name, section.content)

                if evaluation.grade == "fail":
                    status_text.info(f"Improving section {i+1}/{section_count}: {section.name}")
                    follow_up_queries = evaluation.follow_up_queries

                    # Perform follow-up searches
                    additional_results = self._parallel_web_search(follow_up_queries)
                    all_search_results.extend(additional_results)

                    # Update source context and rewrite section
                    source_str = ReportUtils.deduplicate_and_format_sources(
                        all_search_results,
                        return_type="string"
                    )
                    section_content = self.write_section(
                        section.name,
                        section.description,
                        source_str,
                        section.content
                    )
                    section.content = section_content
                    self.sections_content[section.name] = section

                current_progress += section_eval_increment
                progress_bar.progress(int(current_progress))

            # Step 7: Write final sections (85% to 95%)
            status_text.info("Writing introduction and conclusion")
            all_sections_content = "\n\n".join([s.content for s in report_plan.sections])
            introduction = self.write_final_sections("Introduction", all_sections_content)
            conclusion = self.write_final_sections("Conclusion", all_sections_content)
            progress_bar.progress(95)

            # Step 8: Compile final report (95% to 100%)
            status_text.info("Compiling final report")
            all_sections = "\n\n".join([s.content for s in report_plan.sections])

            final_report = f"""
            {introduction}

            {all_sections}

            {conclusion}
            """

            # Append sources
            sources_section = ReportUtils.deduplicate_and_format_sources(
                all_search_results,
                return_type="list"
            )
            sources_section_str = "\n".join(sources_section)
            final_report += f"\n\n### Sources\n{sources_section_str}"

            # Complete progress
            progress_bar.progress(100)
            status_text.success("Research complete!")

            return {"final_report": final_report}

        except Exception as e:
            status_text.error(f"An error occurred: {str(e)}")
            logger.error(f"Error in report generation: {e}", exc_info=True)
            return {"final_report": f"Error generating report: {str(e)}"}

# --------------------------------------------------------------
# Step 6: Streamlit app
# --------------------------------------------------------------

def main():
    """Main function for the Streamlit application."""
    st.set_page_config(
        page_title="Deep Research Pro",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Deep Research Pro")

    with st.sidebar:
        st.title("🔍 Research Assistant")
        st.write("A self-service app that automates the generation of reports and assists in research tasks.")

        st.header("How It Works")
        st.markdown(
            """
    1. Enter your research query below.
    2. (Optional) Upload supplementary files (e.g., PDFs, images) for additional context.
    3. Select your preferred **research engine** and **research depth**.
    4. Click **Start Research** to begin the analysis.
    5. Watch progress in real-time and review the final report with citations.
            """
        )

        engine_choice = st.selectbox(
            "Select Research Engine",
            options=["OpenAI"],
            help="The AI engine that will be used for research and report generation."
        )

        research_depth = st.selectbox(
            "Select Research Depth",
            ["Basic", "In-depth", "Advanced"],
            help="""
            - Basic: Quick research with fewer sources
            - In-depth: More comprehensive research with additional follow-up queries
            - Advanced: Thorough research with maximum sources and quality checks
            """
        )

    # Main content area
    st.markdown("### Enter Your Research Query")
    query = st.text_area(
        "Type your query here...",
        height=150,
        help="Enter a clear, specific research question or topic."
    )

    # File upload with more options
    uploaded_files = st.file_uploader(
        "Upload supporting documents (optional)",
        type=["pdf", "png", "jpg", "docx", "txt", "csv"],
        accept_multiple_files=True,
        help="Upload files that provide additional context for your research."
    )

    col1, col2 = st.columns(2)
    with col1:
        start_button = st.button(
            "Start Research",
            help="Begin the research process. This may take several minutes."
        )

    with col2:
        if uploaded_files:
            st.info(f"Uploaded {len(uploaded_files)} files.")

    report_placeholder = st.empty()

    if start_button:
        if query.strip() == "":
            st.warning("Please provide a query before starting the research.")
        else:
            with st.spinner("Deep Research in progress... This may take 5–30 minutes."):
                try:
                    # Get API keys
                    openai_api_key = st.secrets["openai_api_key"]
                    brave_api_key = st.secrets["brave_api_key"]

                    # Initialize the report generator
                    report_generator = ReportGenerator(
                        openai_api_key=openai_api_key,
                        brave_api_key=brave_api_key
                    )

                    # Generate the report
                    result = report_generator.generate_report(
                        topic=query,
                        report_organization=Prompts.DEFAULT_REPORT_STRUCTURE,
                        context="",
                        feedback=None,
                        research_depth=research_depth
                    )

                    # Output the final report
                    final_report = result["final_report"]
                    report_placeholder.markdown(final_report, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    logger.error(f"Error in main app: {e}", exc_info=True)

if __name__ == "__main__":
    main()

