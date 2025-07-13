# Installation Guide

Follow these steps to set up the application locally.

1. **Clone the repository** and navigate to the project directory.
2. **Create a virtual environment** (Python 3.10 or later is recommended).
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   # optional system packages
   xargs -a packages.txt sudo apt-get install -y
   ```
4. **Configure secrets**:
   - Copy your API keys into `.streamlit/secrets.toml`.
   - Update `config.yaml` with user credentials or environment variables.
5. **Run the app**:
   ```bash
   streamlit run BioGen.py
   ```

For more advanced deployment options, see `docs/Architecture.md`.

