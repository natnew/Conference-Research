# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-07-15

### Added
- **File Upload Validation**: Comprehensive security checks for uploaded files including size limits (50MB), MIME type verification, and filename sanitization
- **API Retry Mechanisms**: Exponential backoff retry logic for all API calls (OpenAI, Google Serper, web scraping)
- **WebDriver Context Managers**: Proper resource management to prevent memory leaks in Course Reading List scraper
- **Enhanced Error Handling**: Specific exception types throughout the application replacing bare `except Exception:` blocks
- **AGENTS.md**: New comprehensive instructions file for AI agent configuration
- **Enhanced Documentation**: Comprehensive docstrings across all modules with detailed parameter descriptions

### Changed
- **Improved Variable and Function Naming**: Standardized naming conventions across all modules for better code readability
- **Enhanced README.md**: Comprehensive updates with improved setup instructions and troubleshooting guides
- **Updated OpenAI API Version**: Latest version for better compatibility and performance
- **Expanded Email Draft Text Area**: Improved user interface for email composition in Outreach tab
- **Column Handling**: Better support for 'Affiliation' vs 'University' column mapping in Desktop Research

### Fixed
- **Bare Exception Handling**: Replaced generic exception catching with specific exception types (OpenAI API errors, WebDriver exceptions, network timeouts)
- **WebDriver Memory Leak Risk**: Implemented proper cleanup using context managers in ReadingListScraper
- **Unvalidated File Uploads**: Added security validation to prevent malicious file uploads
- **TypeError in Deep Research**: Fixed structured response handling for better data processing
- **API Call Failures**: Added retry mechanisms with exponential backoff for improved reliability

### Security
- **File Upload Security**: Validation against malicious file uploads with size, type, and content checks
- **Input Sanitization**: Enhanced validation of all user inputs throughout the application
- **Error Message Security**: Improved error handling to prevent information leakage

### Performance
- **Memory Management**: Fixed WebDriver memory leaks and improved resource cleanup
- **API Efficiency**: Reduced redundant API calls through intelligent retry mechanisms
- **Token Optimization**: Better management of API token usage for cost efficiency

### Technical Improvements
- **Code Architecture**: Added context managers, retry decorators, and validation functions
- **Error Handling**: Comprehensive exception handling with specific error types
- **Documentation**: Enhanced code documentation and user guides
- **Testing**: Better error simulation and edge case handling

## [Unreleased]
- Real-time collaboration features for team research
- Advanced analytics and reporting capabilities
- Mobile-responsive interface improvements
- Additional API integrations for enhanced research capabilities
- Bumped OpenAI client requirement to >=1.30.0 for structured output support

