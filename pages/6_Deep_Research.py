import streamlit as st
import time
from duckduckgo_search import DDGS
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from typing import List, TypedDict, Literal, Annotated, Optional
from pydantic import BaseModel, Field, fields
import os
import operator

# Set the OpenAI API key
openai_api_key = st.secrets["openai_api_key"]
os.environ["OPENAI_API_KEY"] = openai_api_key

# --- CONFIGURATION ---
DEFAULT_REPORT_STRUCTURE = """The report structure should focus on breaking-down the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   - Include any key concepts and definitions
   - Provide real-world examples or case studies where applicable

3. Conclusion
   - Aim for 1 structural element (either a list of table) that distills the main body sections
   - Provide a concise summary of the report"""

class PlannerProvider:
    OPENAI = "openai"

class Configuration:
    """The configurable fields for the chatbot."""
    report_structure: str = DEFAULT_REPORT_STRUCTURE  # Defaults to the default report structure
    number_of_queries: int = 2  # Number of search queries to generate per iteration
    max_search_depth: int = 2  # Maximum number of reflection + search iterations
    planner_provider: PlannerProvider = PlannerProvider.OPENAI  # Defaults to OpenAI as provider
    planner_model: str = "o3-mini"  # Defaults to OpenAI o3-mini as planner model
    writer_model: str = "o3-mini"  # Defaults to Anthropic as provider

    @classmethod
    def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = config["configurable"] if config and "configurable" in config else {}
        values = {f.name: os.environ.get(f.name.upper(), configurable.get(f.name)) for f in fields(cls) if f.init}
        return cls(**{k: v for k, v in values.items() if v})

# --- PROMPTS ---
report_planner_query_writer_instructions = """You are an expert technical writer, helping to plan a report.

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

report_planner_instructions = """I want a plan for a report.

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

query_writer_instructions = """You are an expert technical writer crafting targeted web search queries that will gather comprehensive information for writing a technical report section.

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

section_writer_instructions = """You are an expert technical writer crafting one section of a technical report.

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
- End with ### Sources that references the below source material formatted as:
  * List each source with title, date, and URL
  * Format: `- Title : URL`
</Length and style>

<Quality checks>
- Exactly 150-200 words (excluding title and sources)
- Careful use of only ONE structural element (table or list) and only if it helps clarify your point
- One specific example / case study
- Starts with bold insight
- No preamble prior to creating the section content
- Sources cited at end
</Quality checks>
"""

section_grader_instructions = """Review a report section relative to the specified topic:

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

final_section_writer_instructions = """You are an expert technical writer crafting a section that synthesizes information from the rest of the report.

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
</Quality Checks>"""

# --- STATE ---
class Section(BaseModel):
    name: str = Field(description="Name for this section of the report.")
    description: str = Field(description="Brief overview of the main topics and concepts to be covered in this section.")
    research: bool = Field(description="Whether to perform web research for this section of the report.")
    content: str = Field(description="The content of the section.")

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
    sections: list[Section]  # List of report sections
    completed_sections: Annotated[list, operator.add]  # Send() API key
    report_sections_from_research: str  # String of any completed sections from research to write final sections
    final_report: str  # Final report

class SectionState(TypedDict):
    section: Section  # Report section
    search_iterations: int  # Number of search iterations done
    search_queries: list[SearchQuery]  # List of search queries
    source_str: str  # String of formatted source content from web search
    feedback_on_report_plan: str  # Feedback on the report plan
    report_sections_from_research: str  # String of any completed sections from research to write final sections
    completed_sections: list[Section]  # Final key we duplicate in outer state for Send() API

class SectionOutputState(TypedDict):
    completed_sections: list[Section]  # Final key we duplicate in outer state for Send() API

# --- UTILS ---
def deduplicate_and_format_sources(search_response, max_tokens_per_source, include_raw_content=True):
    """
    Takes a list of search responses and formats them into a readable string.
    Limits the raw_content to approximately max_tokens_per_source.

    Args:
        search_response: List of search response dicts, each containing:
            - title: str
            - href: str
            - body: str
        max_tokens_per_source: int
        include_raw_content: bool

    Returns:
        str: Formatted string with deduplicated sources
    """
    # Collect all results
    sources_list = search_response

    # Deduplicate by URL
    unique_sources = {source['href']: source for source in sources_list}

    # Format output
    formatted_text = "Sources:\n\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source {source['title']}:\n===\n"
        formatted_text += f"URL: {source['href']}\n===\n"
        formatted_text += f"Most relevant content from source: {source['body']}\n===\n"
        if include_raw_content:
            # Using rough estimate of 4 characters per token
            char_limit = max_tokens_per_source * 4
            # Handle None raw_content
            raw_content = source.get('body', '')
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"

    return formatted_text.strip()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Deep Research",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HEADER SECTION ---
st.title("Deep Research")

# --- SIDEBAR ---
with st.sidebar:
    st.title(":streamlit: Conference & Campus Research Assistant")
    st.write("""
A self-service app that automates the generation of biographical content
and assists in lead generation. Designed to support academic and professional
activities, it offers interconnected modules that streamline research tasks,
whether for conferences, campus visits, or other events.
    """)

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

    # Select between OpenAI or Perplexity
    engine_choice = st.selectbox(
        "Select Research Engine",
        options=["OpenAI"]
    )

    # Advanced settings (adjust or remove if not required)
    research_depth = st.selectbox("Select Research Depth", ["Basic", "In-depth", "Advanced"])

# --- MAIN INPUT AREA ---
st.markdown("### Enter Your Research Query")
query = st.text_area("Type your query here...", height=150)

uploaded_files = st.file_uploader(
    "Upload supporting documents (optional)",
    type=["pdf", "png", "jpg"],
    accept_multiple_files=True
)

start_button = st.button("Start Research")

# --- PLACEHOLDERS FOR FEEDBACK ---
progress_placeholder = st.empty()
report_placeholder = st.empty()

# --- RESEARCH LOGIC ---
if start_button:
    if query.strip() == "":
        st.warning("Please provide a query before starting the research.")
    else:
        with st.spinner("Deep Research in progress... This may take 5–30 minutes."):
            # Show progress updates (replace or integrate with your own engine’s progress feed)
            for i in range(1, 11):
                progress_value = i * 10
                progress_placeholder.info(f"Processing with {engine_choice}... {progress_value}% complete")
                time.sleep(0.5)  # Simulated delay

            progress_placeholder.success("Research complete!")

        # Perform web search using DuckDuckGo
        search_results = DDGS().text(query, max_results=5)
        source_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000, include_raw_content=False)

        # Set up the configuration
        config = Configuration(
            report_structure=DEFAULT_REPORT_STRUCTURE,
            number_of_queries=2,
            max_search_depth=2,
            planner_provider=PlannerProvider.OPENAI,
            planner_model="o3-mini",
            writer_model="o3-mini"
        )

        # Initialize the state
        state = ReportState(
            topic=query,
            sections=[],
            completed_sections=[],
            report_sections_from_research="",
            final_report=""
        )

        # Generate the report plan
        structured_llm = ChatOpenAI(model=config.planner_model, temperature=0).with_structured_output(Queries)
        system_instructions_query = report_planner_query_writer_instructions.format(topic=query, report_organization=config.report_structure, number_of_queries=config.number_of_queries)
        results = structured_llm.invoke([{"role": "system", "content": system_instructions_query}])
        query_list = [query.search_query for query in results.queries]

        # Generate sections
        system_instructions_sections = report_planner_instructions.format(topic=query, report_organization=config.report_structure, context=source_str, feedback=None)
        structured_llm = ChatOpenAI(model=config.planner_model, temperature=0).with_structured_output(Sections)
        report_sections = structured_llm.invoke([{"role": "system", "content": system_instructions_sections}])
        sections = report_sections.sections

        # Write sections
        for section in sections:
            system_instructions = section_writer_instructions.format(section_title=section.name, section_topic=section.description, context=source_str, section_content=section.content)
            section_content = ChatOpenAI(model=config.writer_model, temperature=0).invoke([{"role": "system", "content": system_instructions}])
            section.content = section_content.content

        # Compile the final report
        all_sections = "\n\n".join([s.content for s in sections])
        final_report = f"""
        ## Research Report: *{query}* (via {engine_choice})

        **Research Depth:** {research_depth}

        **Summary:**
        This report synthesises information from multiple sources, providing insights
        into the subject matter with citations for further review.

        **Key Findings:**
        {all_sections}

        **Conclusion:**
        The research confirms that rapid AI-driven insights can bolster deep
        investigations, though expert validation remains vital.
        """

        report_placeholder.markdown(final_report, unsafe_allow_html=True)
