# Development Environment Setup Guide

This guide explains how to set up the Conference Research application for development across different operating systems and environments.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/natnew/Conference-Research.git
cd Conference-Research

# Set up development environment (cross-platform)
python scripts/make.py install

# Validate setup
python scripts/make.py validate-env

# Start development server
python scripts/make.py dev
```

## Prerequisites

### Required Software
- **Python 3.9+** (3.11 recommended)
- **Git** for version control
- **Chrome or Chromium** browser for WebDriver tests

### Optional (for advanced development)
- **Docker** for containerized development
- **VS Code** with recommended extensions
- **Poetry** for alternative dependency management

## Installation Methods

### Method 1: Standard Python Setup (Recommended)

1. **Create virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   python scripts/make.py install
   ```

3. **Configure environment:**
   ```bash
   # Copy example environment file
   cp .env.example .env.development
   
   # Edit .env.development with your API keys
   # OPENAI_API_KEY=your_key_here
   # SERPER_API_KEY=your_key_here
   ```

### Method 2: Docker Development Environment

1. **Build development container:**
   ```bash
   docker-compose build
   ```

2. **Start development environment:**
   ```bash
   docker-compose up conference-research
   ```

3. **Access application:**
   - Open http://localhost:8501 in your browser

### Method 3: VS Code Development Containers

1. **Install VS Code extensions:**
   - Dev Containers
   - Python

2. **Open project in container:**
   - `Ctrl+Shift+P` → "Dev Containers: Reopen in Container"

3. **Container will automatically:**
   - Install dependencies
   - Set up development tools
   - Configure debugging

## Configuration

### Environment Variables

Create `.env.development` file:
```bash
# Environment
ENVIRONMENT=development

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serper_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Development Settings
DEBUG_MODE=true
LOG_LEVEL=DEBUG
WEBDRIVER_HEADLESS=false  # Show browser for debugging
```

### Configuration Files

The application uses YAML configuration files:
- `config/base.yaml` - Default settings
- `config/development.yaml` - Development overrides
- `config/testing.yaml` - Test environment settings
- `config/production.yaml` - Production settings

### API Keys Setup

1. **OpenAI API Key:**
   - Sign up at https://platform.openai.com/
   - Generate API key in API Keys section
   - Add to `.env.development`

2. **Google Serper API Key:**
   - Sign up at https://serper.dev/
   - Generate API key
   - Add to `.env.development`

3. **Groq API Key (optional):**
   - Sign up at https://console.groq.com/
   - Generate API key
   - Add to `.env.development`

## Development Workflow

### 1. Daily Development

```bash
# Activate environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Update dependencies
python scripts/make.py deps-update

# Run tests
python scripts/make.py test-fast

# Start development server
python scripts/make.py dev
```

### 2. Code Quality

```bash
# Format code
python scripts/make.py format

# Run linting
python scripts/make.py lint

# Security scan
python scripts/make.py security
```

### 3. Testing

```bash
# Run all tests
python scripts/make.py test

# Run specific test types
python scripts/make.py test-unit
python scripts/make.py test-integration

# Run with debugger
pytest tests/test_file_validation.py -s --pdb
```

## Development Tools

### Available Make Commands

```bash
python scripts/make.py <command>

Available commands:
  install          Set up development environment
  install-prod     Install production dependencies only
  test            Run full test suite with coverage
  test-unit       Run unit tests only
  test-integration Run integration tests only
  test-fast       Run tests without coverage (faster)
  lint            Run code quality checks
  format          Format code and fix issues
  security        Run security scans
  clean           Clean temporary files
  dev             Start development server
  validate-env    Check environment setup
  deps-update     Update dependencies
  help            Show available commands
```

### IDE Setup

#### VS Code (Recommended)

Install extensions:
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.pylint",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker",
        "ms-vscode.test-adapter-converter"
    ]
}
```

Settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm

1. **Open project folder**
2. **Configure Python interpreter:**
   - File → Settings → Project → Python Interpreter
   - Add Local Interpreter → Existing environment
   - Point to `venv/bin/python`

3. **Configure test runner:**
   - File → Settings → Tools → Python Integrated Tools
   - Default test runner: pytest

## Browser Setup for Testing

### Chrome/Chromium Installation

**Windows:**
```bash
# Using Chocolatey
choco install googlechrome chromedriver

# Or download from:
# https://www.google.com/chrome/
# https://chromedriver.chromium.org/
```

**macOS:**
```bash
# Using Homebrew
brew install --cask google-chrome
brew install chromedriver
```

**Ubuntu/Debian:**
```bash
# Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable

# ChromeDriver
sudo apt install chromium-chromedriver
```

### WebDriver Configuration

For development, browsers can run in non-headless mode:
```yaml
# config/development.yaml
webdriver:
  headless: false  # Show browser for debugging
  timeout: 60      # Longer timeout for debugging
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues
```bash
# Check Python version
python --version

# Should be 3.9 or higher
# If not, install correct version:
# Windows: Download from python.org
# macOS: brew install python@3.11
# Linux: sudo apt install python3.11
```

#### 2. Package Installation Failures
```bash
# Clear pip cache
pip cache purge

# Upgrade pip
python -m pip install --upgrade pip

# Reinstall dependencies
python scripts/make.py clean
python scripts/make.py install
```

#### 3. WebDriver Issues
```bash
# Check Chrome installation
google-chrome --version  # Linux/macOS
chrome --version         # Windows

# Update ChromeDriver
pip install --upgrade webdriver-manager

# Test WebDriver manually
python -c "from selenium import webdriver; driver = webdriver.Chrome(); driver.quit()"
```

#### 4. API Key Issues
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $SERPER_API_KEY

# Verify .env.development file exists and has correct keys
cat .env.development
```

#### 5. Import Errors
```bash
# Ensure project is installed in development mode
pip install -e .

# Check PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"
```

### Getting Help

1. **Check environment setup:**
   ```bash
   python scripts/make.py validate-env
   ```

2. **Run diagnostics:**
   ```bash
   python -c "
   import sys
   print(f'Python: {sys.version}')
   import streamlit
   print(f'Streamlit: {streamlit.__version__}')
   import pandas
   print(f'Pandas: {pandas.__version__}')
   "
   ```

3. **Check logs:**
   ```bash
   # Application logs
   tail -f logs/conference_research.log
   
   # Streamlit logs
   streamlit run BioGen.py --logger.level debug
   ```

## Contributing

### Development Process

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes with tests:**
   ```bash
   # Edit code
   # Write tests
   python scripts/make.py test
   ```

3. **Code quality checks:**
   ```bash
   python scripts/make.py lint
   python scripts/make.py format
   python scripts/make.py security
   ```

4. **Submit pull request:**
   ```bash
   git add .
   git commit -m "Add your feature description"
   git push origin feature/your-feature-name
   ```

### Code Standards

- **Python 3.9+ compatibility**
- **Type hints** for function signatures
- **Docstrings** for all public functions
- **Test coverage** ≥70% overall, ≥90% for security functions
- **Security-first** approach for file handling and API calls

### Pre-commit Hooks

Automatically run quality checks:
```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Production Deployment

### Environment Setup

1. **Set production environment:**
   ```bash
   export ENVIRONMENT=production
   ```

2. **Use production configuration:**
   - Headless WebDriver
   - Optimized timeouts
   - Structured logging
   - Caching enabled

3. **Security considerations:**
   - Use environment variables for secrets
   - Enable all validation
   - Monitor API usage
   - Log security events

For detailed deployment instructions, see `docs/DEPLOYMENT.md`.

## Performance Optimization

### Development Performance

1. **Use test configuration:**
   ```bash
   export ENVIRONMENT=testing
   python scripts/make.py test-fast
   ```

2. **Optimize API calls:**
   - Use smaller token limits in development
   - Mock API responses for testing
   - Cache responses when possible

3. **WebDriver optimization:**
   - Use headless mode for automated testing
   - Reuse WebDriver instances when safe
   - Set appropriate timeouts

### Resource Monitoring

```bash
# Check memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"

# Monitor during development
htop  # Linux/macOS
# or use Task Manager on Windows
```

## Next Steps

After setup:

1. **Familiarize with codebase:**
   - Read `README.md`
   - Review `docs/ARCHITECTURE.md`
   - Explore `BioGen.py` main application

2. **Run example workflows:**
   - Upload sample CSV file
   - Generate a bio
   - Test web scraping

3. **Contribute:**
   - Check GitHub issues
   - Review `CONTRIBUTING.md`
   - Join development discussions

For more information, see the [project documentation](https://github.com/natnew/Conference-Research/tree/main/docs).
