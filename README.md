# Conference Research

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![Tests](https://github.com/natnew/Conference-Research/workflows/Test%20Suite/badge.svg)
![Coverage](https://img.shields.io/badge/coverage-70%25+-green.svg)

🔬 **Automated Conference & Campus Research Assistant**

A comprehensive Streamlit application that automates biographical data collection, lead generation, and outreach for academic conferences and campus visits. Built with security, reliability, and developer experience in mind.

## ✨ Key Features

- 🤖 **AI-Powered Bio Generation** - Automated profile creation using OpenAI GPT-4o-mini
- 🔍 **Smart Web Scraping** - Intelligent content extraction with retry mechanisms
- 📊 **Batch Processing** - Handle large datasets with configurable chunking
- 🛡️ **Security-First** - Comprehensive file validation and input sanitization  
- 🔄 **Robust Error Handling** - Automatic retry logic with exponential backoff
- ⚙️ **Environment-Aware Config** - Production-ready configuration management
- 🧪 **Comprehensive Testing** - 70%+ test coverage with CI/CD integration

## 🚀 Quick Start

```bash
# Clone and set up development environment
git clone https://github.com/natnew/Conference-Research.git
cd Conference-Research

# One-command setup (cross-platform)
python scripts/make.py install

# Configure API keys
cp .env.example .env.development
# Edit .env.development with your OpenAI and Serper API keys

# Start the application
python scripts/make.py dev
# Opens http://localhost:8501
```

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [New Features & Improvements](#-new-features--improvements)
3. [Application Pages](#streamlit-pages)
4. [Installation & Setup](#-installation--setup)
5. [Development](#-development)
6. [Testing](#-testing)
7. [Configuration](#-configuration)
8. [Documentation](#documentation)
9. [Contributing](#-contributing)
10. [License](#license)

## 🆕 New Features & Improvements

### 🔒 Security Enhancements
- **File Upload Validation**: Comprehensive security checks for uploaded files
- **Input Sanitization**: Protection against malicious file names and content
- **MIME Type Verification**: Validation of file content vs. declared type
- **Size Limits**: Configurable file size restrictions (default 50MB)

### 🔧 Reliability Improvements  
- **API Retry Logic**: Automatic retries with exponential backoff for API failures
- **Memory Management**: Proper WebDriver cleanup to prevent memory leaks
- **Error Recovery**: Enhanced error handling with specific exception types
- **Configuration Management**: Environment-aware settings with validation

### 🧪 Testing Infrastructure
- **Comprehensive Test Suite**: 70%+ code coverage with unit and integration tests
- **CI/CD Pipeline**: Automated testing across multiple OS and Python versions
- **Security Scanning**: Automated vulnerability detection and dependency checks
- **Performance Monitoring**: Memory usage and performance regression testing

### 🛠️ Developer Experience
- **Modern Dependency Management**: pyproject.toml with locked dependencies
- **Docker Development**: Containerized development environment
- **VS Code Integration**: Development containers and debugging configuration
- **Cross-Platform Scripts**: PowerShell-compatible development commands

## Presentation
### 📹 Video 
### 🗨️ Slides 

## Streamlit Pages

- **[BioGen](BioGen.py)** – AI-powered biographical profile generation with web scraping and batch processing
- **[RAG](pages/2_RAG.py)** – Retrieval-augmented generation for document search and analysis  
- **[Outreach](pages/3_Outreach.py)** – AI-assisted personalized email template creation
- **[Desktop Research](pages/4_Desktop_Research.py)** – Deep internet and local file search capabilities
- **[PDF Extractor](pages/5_PDF_Extractor.py)** – Intelligent text extraction from PDF documents
- **[Deep Research](pages/6_Deep_Research.py)** – Extended background research on selected delegates

### 🔧 Backend Architecture
- **[Configuration Management](con_research/config/)** – Environment-aware settings with validation
- **[Content Scraping](con_research/src/modules/scrapping_module.py)** – Robust web scraping with retry logic
- **[Semantic Search](con_research/src/modules/search_module.py)** – Advanced search using external APIs

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.9+** (3.11 recommended)
- **Chrome/Chromium browser** (for WebDriver functionality)
- **API Keys**: OpenAI and Google Serper API keys

### Quick Installation
```bash
# Method 1: Standard Setup
git clone https://github.com/natnew/Conference-Research.git
cd Conference-Research
python scripts/make.py install

# Method 2: Docker Development  
docker-compose up conference-research

# Method 3: VS Code Dev Containers
# Open in VS Code → "Reopen in Container"
```

### Configuration
1. **Copy environment template:**
   ```bash
   cp .env.example .env.development
   ```

2. **Add your API keys to `.env.development`:**
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   ```

3. **Validate setup:**
   ```bash
   python scripts/make.py validate-env
   ```

### Environment-Specific Configuration
- **Development**: Relaxed validation, visible browser, debug logging
- **Testing**: Fast timeouts, strict validation, minimal logging  
- **Production**: Optimized settings, headless browser, structured logging

## 🧪 Testing

### Running Tests
```bash
# Full test suite with coverage
python scripts/make.py test

# Fast tests (no coverage)
python scripts/make.py test-fast

# Specific test types
python scripts/make.py test-unit
python scripts/make.py test-integration
```

### Test Coverage
- **Overall**: 70%+ coverage required
- **Security Functions**: 90%+ coverage (file validation, API retry)
- **CI/CD**: Automated testing on every pull request

### Test Types
- **Unit Tests**: Individual function testing with mocks
- **Integration Tests**: Component interaction testing
- **Security Tests**: Vulnerability and input validation testing
- **Performance Tests**: Memory usage and timing validation

## ⚙️ Configuration

### Configuration Hierarchy
1. **Base Configuration** (`config/base.yaml`) - Default settings
2. **Environment Override** (`config/{environment}.yaml`) - Environment-specific
3. **Environment Variables** - Runtime overrides
4. **Secrets Management** - Secure credential storage

### Key Configuration Areas
- **API Settings**: Timeouts, retry logic, model selection
- **File Upload**: Size limits, allowed types, security validation
- **WebDriver**: Browser settings, timeouts, user agents
- **Logging**: Levels, formats, file output

## 🔧 Development

### Development Commands
```bash
# Setup and validation
python scripts/make.py install        # Full development setup
python scripts/make.py validate-env   # Check environment

# Code quality
python scripts/make.py format         # Format code (black, ruff)
python scripts/make.py lint          # Run linting checks
python scripts/make.py security      # Security scans

# Development workflow  
python scripts/make.py dev           # Start development server
python scripts/make.py clean         # Clean temporary files
python scripts/make.py deps-update   # Update dependencies
```

### Development Tools
- **Black**: Code formatting
- **Ruff**: Fast Python linting 
- **MyPy**: Static type checking
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks for quality checks

### Docker Development
```bash
# Build and start development environment
docker-compose up --build

# Access development tools container
docker-compose run dev-tools bash

# View logs
docker-compose logs -f conference-research
```

## 📚 Documentation

Comprehensive documentation available in `/docs/`:

- **[Installation Guide](docs/DEVELOPMENT.md)** - Detailed setup instructions
- **[Testing Guide](docs/TESTING.md)** - Test writing and execution
- **[Configuration Guide](docs/CONFIGURATION.md)** - Settings management
- **[User Guide](reports/User_Guide.md)** - Application usage instructions
- **[Architecture Overview](docs/Architecture.md)** - System design and components

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](Contributing.md) for details.

### Development Process
1. **Fork and clone** the repository
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** with tests and documentation
4. **Run quality checks**: `python scripts/make.py lint`
5. **Submit pull request** with clear description

### Code Standards
- **Python 3.9+** compatibility
- **Type hints** for function signatures  
- **Comprehensive tests** (70%+ coverage)
- **Security-first** approach
- **Clear documentation** and docstrings

### Review Checklist
- [ ] Tests pass and maintain coverage
- [ ] Code follows style guidelines
- [ ] Security considerations addressed
- [ ] Documentation updated
- [ ] Performance impact considered

## 🔐 Security

### Security Features
- **Input Validation**: All user inputs sanitized and validated
- **File Security**: Comprehensive upload validation and MIME type checking
- **API Security**: Rate limiting and secure credential management
- **Error Handling**: No sensitive information in error messages

### Reporting Security Issues
Please report security vulnerabilities to [security@conference-research.com](mailto:security@conference-research.com) or through GitHub's security advisory system.

## 📊 Performance

### Optimization Features
- **Batch Processing**: Configurable chunk sizes for large datasets
- **Caching**: Response caching for repeated queries (configurable)
- **Memory Management**: Proper resource cleanup and monitoring
- **API Efficiency**: Token optimization and request batching

### Monitoring
- **Memory Usage**: Automatic monitoring during processing
- **API Costs**: Token usage tracking and reporting
- **Performance Metrics**: Processing time and throughput monitoring

## 🚀 Deployment

### Production Deployment
```bash
# Set production environment
export ENVIRONMENT=production

# Use production configuration
# - Headless WebDriver
# - Optimized timeouts  
# - Structured logging
# - Enhanced security

# Deploy with Docker
docker-compose -f docker-compose.prod.yml up
```

### Cloud Deployment
- **Streamlit Cloud**: Direct deployment from GitHub
- **AWS/Azure**: Container deployment with managed secrets
- **Heroku**: Git-based deployment with buildpacks

For detailed deployment instructions, see `docs/DEPLOYMENT.md`.

## 🔄 Recent Updates

### Version 2.0.0 (Latest)
- ✅ **Comprehensive Testing Infrastructure** - 70%+ coverage, CI/CD pipeline
- ✅ **Modern Dependency Management** - pyproject.toml, locked dependencies  
- ✅ **Configuration Management** - Environment-aware settings with validation
- ✅ **Security Enhancements** - File validation, input sanitization, retry logic
- ✅ **Developer Experience** - Docker support, VS Code integration, cross-platform scripts

### Previous Versions
- **1.x**: Basic functionality with manual configuration
- **0.x**: Initial prototype and proof of concept

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o-mini API
- **Google** for Serper search API  
- **Streamlit** for the web application framework
- **Open Source Community** for the excellent Python ecosystem

## 📞 Support

- **Documentation**: Check `/docs/` directory
- **Issues**: Submit via GitHub Issues
- **Questions**: Start a GitHub Discussion
- **Email**: [support@conference-research.com](mailto:support@conference-research.com)

---

Built with ❤️ by [Natasha Newbold](https://www.linkedin.com/in/natasha-newbold/) and the Conference Research community.
