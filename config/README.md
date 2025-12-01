# Environment Configuration README

This directory contains environment-specific configuration files for the ML Visualizer application.

## Available Environments

- **development.env**: Local development configuration with debug mode and hot reload
- **testing.env**: Testing/QA environment configuration
- **staging.env**: Pre-production staging environment
- **production.env**: Production environment with security hardening

## Usage

### Docker Compose
The environment files are automatically loaded by docker-compose:

```bash
# Development
docker-compose -f docker-compose.dev.yml up

# Testing
docker-compose -f docker-compose.test.yml up

# Staging
docker-compose -f docker-compose.staging.yml up

# Production
docker-compose -f docker-compose.prod.yml up
```

### Manual Loading
To load environment variables manually:

```bash
# Load environment
source config/development.env

# Or export all variables
export $(cat config/production.env | xargs)
```

### Azure Deployment
Environment variables are configured in Azure App Service settings via:
- GitHub Actions workflows (CI/CD)
- Bicep templates (Infrastructure as Code)
- Azure Portal (Manual configuration)

## Configuration Variables

### Core Settings
- `ENVIRONMENT_NAME`: Environment identifier (development, testing, staging, production)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `ENABLE_DEBUG_MODE`: Enable debug features
- `MAX_CONCURRENT_USERS`: Maximum concurrent user limit

### Feature Flags
- `ENABLE_FEATURE_FLAGS`: Enable feature flag system
- `EXPERIMENTAL_FEATURES`: Allow experimental features
- `ENABLE_TEST_ENDPOINTS`: Expose testing endpoints

### Streamlit Configuration
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server
- `STREAMLIT_SERVER_ADDRESS`: Bind address
- `STREAMLIT_SERVER_HEADLESS`: Run in headless mode
- `STREAMLIT_SERVER_RUN_ON_SAVE`: Auto-reload on file changes (dev only)

### Security
- `SECURITY_HEADERS`: Enable security headers (production)
- `SSL_REDIRECT`: Force HTTPS redirects
- `ENABLE_CORS`: Cross-Origin Resource Sharing

### Monitoring
- `MONITORING_ENABLED`: Enable application monitoring
- `PERFORMANCE_MONITORING`: Track performance metrics
- `ERROR_TRACKING`: Enable error tracking

## Adding New Variables

1. Add the variable to all environment files with appropriate values
2. Update `src/utils/config.py` to expose the variable
3. Document the variable in this README
4. Update Azure App Service configuration if needed

## Security Notes

⚠️ **Never commit sensitive data (passwords, API keys, secrets) to these files!**

Use Azure Key Vault or GitHub Secrets for sensitive configuration:
- Database connection strings
- API keys
- Service credentials
- Encryption keys

## Example: Adding a New Variable

```bash
# In config/production.env
NEW_FEATURE_ENABLED=true
NEW_FEATURE_TIMEOUT=300

# In src/utils/config.py
def get_new_feature_enabled() -> bool:
    return get_config("NEW_FEATURE_ENABLED", "false").lower() == "true"
```
