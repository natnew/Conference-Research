# Conference Research Application - Development Environment
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=development

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Chrome/Chromium for Selenium WebDriver
    chromium \
    chromium-driver \
    # Development tools
    git \
    curl \
    wget \
    # Build dependencies
    gcc \
    g++ \
    make \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash developer
USER developer
WORKDIR /home/developer/app

# Set up Python environment
ENV PATH="/home/developer/.local/bin:$PATH"

# Install Poetry for dependency management
RUN pip install --user poetry
RUN poetry config virtualenvs.create false

# Copy dependency files
COPY --chown=developer:developer pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN poetry install --with dev,test,docs

# Copy application code
COPY --chown=developer:developer . .

# Install the application in development mode
RUN pip install -e .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command for development
CMD ["streamlit", "run", "BioGen.py", "--server.address", "0.0.0.0", "--server.port", "8501", "--server.headless", "true"]
