# Copilot Instructions - Conference Research Application

This is a Python-based Streamlit application designed to automate conference and campus research workflows, including biographical profile generation, lead generation, academic research automation, and outreach email creation. The application integrates multiple APIs (OpenAI, Google Serper, DuckDuckGo) and provides web scraping capabilities for comprehensive academic research.

---

## Code Standards

### Required Before Each Commit

- **Code Quality Checks:**
  - Run `pip install -r requirements.txt` to ensure all dependencies are properly installed
  - Verify all imports are resolved and no missing dependencies exist
  - Test file upload validation with various file types and sizes
  - Ensure API retry mechanisms are functioning correctly

- **Error Handling Validation:**
  - No bare `except Exception:` blocks - use specific exception types
  - All API calls must include retry logic with exponential backoff
  - WebDriver instances must use context managers for proper cleanup
  - File uploads must pass security validation checks

- **Documentation Requirements:**
  - All functions must have comprehensive docstrings with parameter descriptions
  - Include return types and exception documentation
  - Update relevant markdown files (README.md, User_Guide.md) if functionality changes
  - Add comments for complex logic or API integrations

- **Security Compliance:**
  - File upload validation must check size, type, and content
  - All user inputs must be sanitized and validated
  - API keys must be stored in Streamlit secrets, never hardcoded
  - No sensitive information in error messages or logs

### Development Flow

1. **Before Starting Development:**
   - Pull latest changes: `git pull origin main`
   - Check for open GitHub issues to address
   - Review existing code structure and naming conventions

2. **During Development:**
   - Follow established naming conventions (descriptive function and variable names)
   - Use context managers for resource management (WebDrivers, file handles)
   - Implement retry logic for all external API calls
   - Add appropriate error handling with specific exception types

3. **Before Committing:**
   - Test all modified functionality thoroughly
   - Verify error handling works correctly
   - Check that WebDriver instances are properly cleaned up
   - Ensure file validation is working as expected
   - Update documentation if needed

4. **Commit Process:**
   - Use descriptive commit messages referencing issue numbers when applicable
   - Include summary of changes, files modified, and issues resolved
   - Push changes: `git push origin main`

---

## Repository Structure

```
Conference-Research/
├── BioGen.py                     # Main biographical profile generator
├── pages/                        # Streamlit multi-page components
│   ├── 2_RAG.py                 # Retrieval-Augmented Generation for lead filtering
│   ├── 3_Outreach.py            # Email drafting and enhancement
│   ├── 4_Desktop_Research.py    # Academic profile search functionality
│   ├── 5_PDF_Extractor.py       # PDF processing utilities
│   ├── 6_Deep_Research.py       # Advanced research capabilities
│   ├── 7_Dynamic_MultiPage.py   # Dynamic page generation
│   ├── Course_Catalogue.py      # University course catalog scraping
│   ├── Course_Reading List.py   # Reading list extraction and processing
│   └── Web_Scraper.py           # General web scraping utilities
├── con_research/                 # Core research modules
│   └── src/modules/             # Modular functionality
├── reports/                      # Documentation and guides
│   ├── User_Guide.md            # Comprehensive user documentation
│   └── project_report_*.md      # Technical and client reports
├── requirements.txt              # Python dependencies
├── CHANGELOG.md                  # Version history and changes
├── README.md                     # Project overview and setup
└── AGENTS.md                     # AI agent configuration instructions
```

---

## Key Guidelines

### **API Integration Standards:**
- **OpenAI API:** Use GPT-4o-mini-2024-07-18 for cost-effective bio generation
- **Google Serper API:** Implement search with retry logic and rate limiting
- **DuckDuckGo Search:** Use for supplementary research when Serper is unavailable
- **All APIs:** Must include timeout configurations and proper error handling

### **File Processing Requirements:**
- **Supported Formats:** CSV (.csv), Excel (.xlsx, .xls) only
- **Size Limits:** Maximum 50MB per file
- **Required Columns:** 'Name', 'University' (or 'Affiliation')
- **Validation:** Real-time feedback on file validation status
- **Security:** MIME type verification and filename sanitization

### **Web Scraping Best Practices:**
- **WebDriver Management:** Always use context managers (`with` statements)
- **Resource Cleanup:** Ensure proper disposal of browser instances
- **Error Recovery:** Handle timeouts, connection errors, and HTTP errors
- **User-Agent:** Include appropriate headers to prevent blocking
- **Timeout Settings:** Configure reasonable timeouts to prevent hanging

### **Error Handling Patterns:**
- **Specific Exceptions:** Use `requests.RequestException`, `openai.OpenAIError`, `WebDriverException`
- **Retry Logic:** Implement exponential backoff for transient failures
- **User Feedback:** Provide clear, actionable error messages
- **Logging:** Include context for debugging without exposing sensitive data

### **Code Organization:**
- **Function Naming:** Use descriptive names (e.g., `generate_enriched_text`, `validate_file_upload`)
- **Variable Naming:** Clear, consistent naming (e.g., `researcher_full_name`, `university_affiliation`)
- **Module Structure:** Group related functionality in logical modules
- **Documentation:** Maintain up-to-date docstrings and comments

### **Security & Validation:**
- **Input Sanitization:** Validate all user inputs before processing
- **File Security:** Check for malicious patterns in filenames and content
- **API Security:** Store keys securely, implement rate limiting
- **Error Messages:** Avoid exposing internal system information

### **Testing & Quality Assurance:**
- **Manual Testing:** Test file uploads, API calls, and error scenarios
- **Edge Cases:** Handle empty files, malformed data, network failures
- **Performance:** Monitor API usage and optimize for cost efficiency
- **User Experience:** Ensure clear feedback and intuitive workflows

### **Documentation Maintenance:**
- **Keep Updated:** Sync code changes with documentation
- **User Guide:** Reflect new features and security improvements
- **Technical Docs:** Update API references and architecture notes
- **Change Logs:** Document all significant changes and bug fixes
