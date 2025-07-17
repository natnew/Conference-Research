# Implement Configuration Management System

## 🎯 Problem Statement

The Conference Research application currently relies heavily on Streamlit's `st.secrets` for configuration management, which creates several issues:

1. **Hardcoded configuration** scattered throughout the codebase makes changes difficult
2. **No environment-specific settings** - same configuration for development, testing, and production
3. **Secret management limitations** - API keys mixed with regular configuration
4. **No configuration validation** - invalid settings can cause runtime failures
5. **Difficult local development** - developers must manually configure secrets
6. **No configuration documentation** - unclear what settings are required/optional

This makes the application difficult to deploy in different environments and creates barriers for local development and testing.

## 📋 Acceptance Criteria

### Centralized Configuration System
- [ ] **Create configuration hierarchy**: Default settings → Environment files → Environment variables → Secrets
- [ ] **Implement `config.py` module** with structured configuration classes
- [ ] **Add environment detection** (development, testing, production) with appropriate defaults
- [ ] **Support multiple configuration sources** with clear precedence rules
- [ ] **Validate configuration** on application startup with helpful error messages

### Environment-Specific Configuration
- [ ] **Development configuration** (`config/development.yaml`)
  - Local API endpoints and test keys
  - Relaxed timeouts and debugging features
  - Mock services for offline development
- [ ] **Testing configuration** (`config/testing.yaml`)
  - Test database connections
  - Mock API responses
  - Faster timeouts for test speed
- [ ] **Production configuration** (`config/production.yaml`)
  - Production API endpoints
  - Optimized timeouts and retry settings
  - Security-focused defaults

### Secure Secret Management
- [ ] **Separate secrets from configuration** - API keys, passwords, tokens in secure storage
- [ ] **Support multiple secret sources**: Environment variables, AWS Secrets Manager, Azure Key Vault, local files
- [ ] **Secret validation and rotation** - check for expired or invalid credentials
- [ ] **Development secret management** - safe defaults and mock keys for local development

### Configuration Documentation and Validation
- [ ] **Schema validation** using Pydantic or similar for type safety and validation
- [ ] **Configuration documentation** with examples and descriptions for each setting
- [ ] **Startup validation** - fail fast with clear error messages for missing/invalid configuration
- [ ] **Configuration testing** - automated tests for different configuration scenarios

## 📁 Files to Add/Update

### New Configuration Structure:
```
config/
├── __init__.py
├── base.py                              # Base configuration classes and schemas
├── development.yaml                     # Development environment settings
├── testing.yaml                         # Testing environment settings
├── production.yaml                      # Production environment settings
├── schema.py                            # Configuration validation schemas
└── secrets.yaml.example                 # Example secrets file (not committed)

con_research/
├── config/
│   ├── __init__.py
│   ├── config_manager.py                # Central configuration management
│   ├── environment.py                   # Environment detection and loading
│   ├── secrets_manager.py               # Secure secret handling
│   └── validation.py                    # Configuration validation logic

# Environment-specific configurations
.env.example                             # Example environment variables
.env.development                         # Development environment variables
.env.testing                             # Testing environment variables

# Documentation
docs/
├── CONFIGURATION.md                     # Configuration guide
├── DEPLOYMENT.md                        # Deployment configuration guide
└── SECRETS_MANAGEMENT.md                # Secret handling documentation
```

### Files to Update:
- **`BioGen.py`** - Replace `st.secrets` calls with new configuration system
- **`pages/*.py`** - Update all pages to use centralized configuration
- **`con_research/src/modules/*.py`** - Replace hardcoded settings with configuration
- **`requirements.txt`** - Add configuration management dependencies
- **`.gitignore`** - Add secret files and environment-specific configs
- **`README.md`** - Update with configuration setup instructions

## 🔧 Implementation Details

### Configuration Manager Architecture:
```python
# con_research/config/config_manager.py
from typing import Dict, Any, Optional
from pathlib import Path
import yaml
from pydantic import BaseSettings, validator

class AppConfig(BaseSettings):
    """Main application configuration with validation"""
    
    # API Configuration
    openai_model: str = "gpt-4o-mini-2024-07-18"
    openai_max_tokens: int = 1000
    openai_timeout: int = 30
    
    # Google Serper Configuration
    serper_timeout: int = 10
    serper_max_results: int = 10
    
    # File Upload Configuration
    max_file_size_mb: int = 50
    allowed_file_types: List[str] = [".csv", ".xlsx", ".xls"]
    
    # WebDriver Configuration
    webdriver_timeout: int = 30
    webdriver_headless: bool = True
    
    # Retry Configuration
    api_retry_attempts: int = 3
    api_retry_delay: float = 1.0
    api_retry_backoff: float = 2.0
    
    @validator('max_file_size_mb')
    def validate_file_size(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('File size must be between 1 and 100 MB')
        return v
    
    class Config:
        env_prefix = "CONFERENCE_RESEARCH_"
        case_sensitive = False

class ConfigManager:
    """Centralized configuration management"""
    
    def __init__(self, environment: str = None):
        self.environment = environment or self._detect_environment()
        self.config = self._load_configuration()
        self.secrets = self._load_secrets()
    
    def _detect_environment(self) -> str:
        """Detect current environment"""
        # Check environment variable, Streamlit context, etc.
        return os.getenv("ENVIRONMENT", "development")
    
    def _load_configuration(self) -> AppConfig:
        """Load configuration from multiple sources"""
        # Load base config, then environment-specific overrides
        pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with fallback"""
        pass
```

### Environment Configuration Example:
```yaml
# config/development.yaml
api:
  openai:
    model: "gpt-4o-mini-2024-07-18"
    max_tokens: 1000
    timeout: 30
    mock_responses: true  # Use mock responses for development
  
  google_serper:
    timeout: 10
    max_results: 5
    mock_responses: true
  
file_upload:
  max_size_mb: 10  # Smaller limit for development
  validation_strict: false
  
webdriver:
  headless: false  # Show browser in development
  timeout: 60  # Longer timeout for debugging
  
logging:
  level: "DEBUG"
  format: "detailed"
```

### Secret Management:
```python
# con_research/config/secrets_manager.py
class SecretsManager:
    """Secure secret management across different environments"""
    
    def __init__(self, environment: str):
        self.environment = environment
        self.secrets_source = self._get_secrets_source()
    
    def _get_secrets_source(self):
        """Determine where to load secrets from based on environment"""
        if self.environment == "production":
            return self._get_cloud_secrets()  # AWS Secrets Manager, etc.
        elif self.environment == "testing":
            return self._get_test_secrets()   # Mock or test-specific secrets
        else:
            return self._get_development_secrets()  # Local files or env vars
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get secret value with appropriate source"""
        pass
```

## 📊 Success Metrics

### Configuration Management:
- [ ] **Zero hardcoded configuration** in application code
- [ ] **Environment-specific deployment** works without code changes
- [ ] **Configuration validation** catches 100% of invalid settings at startup
- [ ] **Secret rotation** can be performed without application changes

### Developer Experience:
- [ ] **One-command environment setup** - `make configure-dev`
- [ ] **Clear configuration errors** with actionable error messages
- [ ] **Local development** works without production secrets
- [ ] **Configuration documentation** covers all settings with examples

### Security and Reliability:
- [ ] **No secrets in version control** or logs
- [ ] **Secure secret storage** in production environments
- [ ] **Configuration drift detection** - verify production config matches expected state
- [ ] **Graceful degradation** when optional services are unavailable

## 🔧 Implementation Phases

### Phase 1: Core Configuration System (Week 1)
1. Create configuration schema and validation
2. Implement ConfigManager with basic environment detection
3. Replace critical `st.secrets` usage in main application
4. Add configuration validation to startup

### Phase 2: Environment-Specific Configs (Week 2)
1. Create environment-specific configuration files
2. Implement secure secrets management
3. Add development and testing configurations
4. Update deployment documentation

### Phase 3: Advanced Features (Week 3)
1. Add configuration hot-reloading for development
2. Implement configuration drift monitoring
3. Add configuration backup and restoration
4. Create configuration management CLI tools

## 🚨 Migration Strategy

### Backwards Compatibility:
- **Phase migration** - gradually replace `st.secrets` usage
- **Fallback support** - maintain compatibility with existing secret structure
- **Migration scripts** - automated conversion of existing configurations
- **Documentation updates** - clear migration guide for deployments

### Risk Mitigation:
- **Extensive testing** of configuration loading in different environments
- **Rollback capability** - ability to revert to previous configuration approach
- **Monitoring and alerting** for configuration-related failures
- **Staged deployment** - test in development/staging before production

## 🔗 Dependencies

### Requires:
- **Environment standardization** - clear development/testing/production environments
- **Secret management infrastructure** - cloud secrets or secure local storage

### Enables:
- **Multi-environment deployment** - easy deployment to different environments
- **Better testing** - isolated test configurations
- **Security improvements** - proper secret management
- **Operational excellence** - configuration monitoring and management

## 💡 Additional Benefits

### Operational Benefits:
- **Easier troubleshooting** - centralized configuration inspection
- **Better monitoring** - configuration-aware logging and metrics
- **Disaster recovery** - configuration backup and restoration
- **Compliance** - auditable configuration changes

### Development Benefits:
- **Faster onboarding** - clear configuration structure
- **Better testing** - environment-specific test configurations
- **Debugging support** - configuration-aware error messages
- **Feature flags** - configuration-driven feature enablement

## 📖 Context

Current `st.secrets` approach creates several pain points:
1. Hard to manage different environments (dev/test/prod)
2. API keys mixed with application settings
3. No validation of configuration values
4. Difficult to track configuration changes
5. Barriers to automated testing and deployment

This configuration management system will provide a solid foundation for scaling the application across different environments while maintaining security and operational excellence.
