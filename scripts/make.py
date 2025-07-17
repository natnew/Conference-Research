"""
Makefile equivalent for Windows PowerShell and cross-platform development
To use: python scripts/make.py <command>
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors."""
    if description:
        print(f"\n🔄 {description}")
    
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=False)
    
    if result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    else:
        print(f"✅ {description or 'Command completed successfully'}")

def install():
    """Install all dependencies and set up development environment."""
    print("🚀 Setting up Conference Research development environment...")
    
    # Upgrade pip
    run_command("python -m pip install --upgrade pip", "Upgrading pip")
    
    # Install the package in development mode with all extras
    run_command("pip install -e .[dev,test,docs,security]", "Installing dependencies")
    
    # Install pre-commit hooks
    run_command("pre-commit install", "Setting up pre-commit hooks")
    
    print("\n✅ Development environment setup complete!")
    print("📖 Run 'python scripts/make.py help' to see available commands")

def install_prod():
    """Install production dependencies only."""
    print("📦 Installing production dependencies...")
    run_command("pip install -e .", "Installing production dependencies")

def test():
    """Run the full test suite."""
    print("🧪 Running test suite...")
    run_command("pytest tests/ -v --cov=con_research --cov=pages --cov-report=term-missing --cov-report=html", "Running tests with coverage")

def test_unit():
    """Run unit tests only."""
    print("🧪 Running unit tests...")
    run_command("pytest tests/ -v -m unit", "Running unit tests")

def test_integration():
    """Run integration tests only."""
    print("🧪 Running integration tests...")
    run_command("pytest tests/ -v -m integration", "Running integration tests")

def test_fast():
    """Run tests without coverage for faster execution."""
    print("⚡ Running fast tests...")
    run_command("pytest tests/ -v --no-cov", "Running tests without coverage")

def lint():
    """Run code quality checks."""
    print("🔍 Running code quality checks...")
    
    # Format check
    run_command("black --check --diff .", "Checking code formatting")
    
    # Lint check
    run_command("ruff check .", "Running linter")
    
    # Type check
    run_command("mypy con_research pages --ignore-missing-imports", "Running type checker")

def format_code():
    """Format code with black and ruff."""
    print("🎨 Formatting code...")
    
    # Format with black
    run_command("black .", "Formatting code with black")
    
    # Fix with ruff
    run_command("ruff check --fix .", "Fixing issues with ruff")

def security():
    """Run security checks."""
    print("🔒 Running security checks...")
    
    # Safety check for known vulnerabilities
    run_command("safety check", "Checking for known vulnerabilities")
    
    # Bandit security scan
    run_command("bandit -r con_research pages", "Running security scan")

def clean():
    """Clean up temporary files and caches."""
    print("🧹 Cleaning up temporary files...")
    
    # Python cache
    patterns_to_remove = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.pytest_cache",
        "**/.mypy_cache",
        "**/.ruff_cache",
        ".coverage",
        "htmlcov",
        "*.egg-info",
        "build",
        "dist",
        ".tox"
    ]
    
    for pattern in patterns_to_remove:
        for path in Path(".").glob(pattern):
            if path.is_file():
                path.unlink()
                print(f"Removed file: {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {path}")

def dev():
    """Start development server."""
    print("🚀 Starting development server...")
    run_command("streamlit run BioGen.py", "Starting Streamlit development server")

def validate_env():
    """Validate development environment setup."""
    print("🔧 Validating development environment...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 9):
        print(f"❌ Python {python_version.major}.{python_version.minor} is not supported. Please use Python 3.9+")
        sys.exit(1)
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if key packages are installed
    required_packages = ["streamlit", "pandas", "openai", "selenium", "pytest"]
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
    
    # Check for Chrome/Chromium (required for Selenium)
    chrome_commands = ["google-chrome --version", "chromium --version", "chrome --version"]
    chrome_found = False
    for cmd in chrome_commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Chrome/Chromium found: {result.stdout.strip()}")
                chrome_found = True
                break
        except:
            continue
    
    if not chrome_found:
        print("⚠️  Chrome/Chromium not found. WebDriver tests may fail.")
    
    print("\n✅ Environment validation complete!")

def deps_update():
    """Update dependencies to latest versions."""
    print("📦 Updating dependencies...")
    run_command("pip install --upgrade --upgrade-strategy eager -e .[dev,test,docs,security]", "Updating all dependencies")

def docs():
    """Build documentation."""
    print("📚 Building documentation...")
    if not Path("docs").exists():
        print("📁 Creating docs directory...")
        Path("docs").mkdir()
        
    # For now, just validate that all markdown files are readable
    markdown_files = list(Path(".").glob("**/*.md"))
    print(f"📄 Found {len(markdown_files)} markdown files")
    for md_file in markdown_files:
        try:
            md_file.read_text(encoding='utf-8')
            print(f"✅ {md_file}")
        except Exception as e:
            print(f"❌ {md_file}: {e}")

def help_cmd():
    """Show available commands."""
    commands = {
        "install": "Install all dependencies and set up development environment",
        "install-prod": "Install production dependencies only",
        "test": "Run the full test suite with coverage",
        "test-unit": "Run unit tests only",
        "test-integration": "Run integration tests only", 
        "test-fast": "Run tests without coverage (faster)",
        "lint": "Run code quality checks (black, ruff, mypy)",
        "format": "Format code with black and fix issues with ruff",
        "security": "Run security checks (safety, bandit)",
        "clean": "Clean up temporary files and caches",
        "dev": "Start development server (Streamlit)",
        "validate-env": "Validate development environment setup",
        "deps-update": "Update dependencies to latest versions",
        "docs": "Build/validate documentation",
        "help": "Show this help message"
    }
    
    print("🛠️  Conference Research Development Commands")
    print("=" * 50)
    print("Usage: python scripts/make.py <command>")
    print()
    
    for cmd, desc in commands.items():
        print(f"  {cmd:<15} {desc}")
    
    print("\n📖 Example workflow:")
    print("  python scripts/make.py install      # Set up environment")
    print("  python scripts/make.py validate-env # Check setup")
    print("  python scripts/make.py test         # Run tests")
    print("  python scripts/make.py dev          # Start development server")

def main():
    """Main command dispatcher."""
    if len(sys.argv) < 2:
        help_cmd()
        return
    
    command = sys.argv[1].replace('-', '_')
    
    commands = {
        "install": install,
        "install_prod": install_prod,
        "test": test,
        "test_unit": test_unit,
        "test_integration": test_integration,
        "test_fast": test_fast,
        "lint": lint,
        "format": format_code,
        "security": security,
        "clean": clean,
        "dev": dev,
        "validate_env": validate_env,
        "deps_update": deps_update,
        "docs": docs,
        "help": help_cmd
    }
    
    if command in commands:
        try:
            commands[command]()
        except KeyboardInterrupt:
            print("\n⚠️  Command interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Command failed: {e}")
            sys.exit(1)
    else:
        print(f"❌ Unknown command: {sys.argv[1]}")
        print("Run 'python scripts/make.py help' to see available commands")
        sys.exit(1)

if __name__ == "__main__":
    main()
