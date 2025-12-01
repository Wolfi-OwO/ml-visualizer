# ML Visualizer - Interactive Machine Learning Demonstrations

A production-ready web application for visualizing machine learning algorithms including Gradient Descent, Perceptron, KNN, and Neural Networks. Built with Streamlit and deployed on Azure with complete CI/CD pipelines.

[![CI](https://github.com/your-repo/actions/workflows/ci.yml/badge.svg)](https://github.com/your-repo/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- Interactive real-time ML algorithm demonstrations
- Multiple algorithms: Gradient Descent, Perceptron, KNN, Neural Networks
- Production-ready with multi-stage Docker builds and auto-scaling
- Complete CI/CD pipeline with automated testing and deployment
- Three environments: Testing, Staging, and Production
- Infrastructure as Code using Azure Bicep templates
- Comprehensive monitoring with Application Insights and alerts

## Quick Start

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd Datascience-ArtificialIntelligence-Webpage

# Start with Docker Compose (recommended)
docker compose -f docker-compose.dev.yml up

# Or without Docker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run src/app.py
```

Visit http://localhost:8501

### Run Tests

```bash
pip install -r requirements.txt
pytest tests/ -v --cov=src --cov-report=html
```

## Project Structure

```
.
├── .github/workflows/      # CI/CD pipelines
├── config/                 # Environment configurations
├── infrastructure/         # Azure Bicep IaC templates
├── src/                    # Application source code
│   ├── app.py              # Main entry point
│   ├── pages/              # ML visualization pages
│   └── utils/              # Configuration and utilities
├── tests/                  # Test suite
├── docker/                 # Docker configurations
├── Dockerfile              # Production Docker image
└── docker-compose.*.yml    # Environment-specific compose files
```

## Deployment Environments

| Environment | Branch   | Auto-Deploy | Approval Required |
|------------|----------|-------------|-------------------|
| Testing    | develop  | Yes         | No                |
| Staging    | staging  | Yes         | No                |
| Production | main     | Yes         | Yes               |

## Architecture

### Deployment Flow
```
feature/* → develop → staging → main
           (testing) (staging) (production)
```

### Infrastructure Components
- Azure Container Registry: Docker image storage
- Azure App Service: Application hosting with auto-scaling
- Application Insights: Monitoring and analytics
- Log Analytics: Centralized logging
- Automated alerts: CPU, memory, errors, response time

### Auto-Scaling Configuration
- Scale out when CPU > 70% or Memory > 80%
- Scale in when CPU < 30% for 10 minutes
- Instance limits per environment:
  - Testing: 1-3 instances
  - Staging: 1-5 instances
  - Production: 2-10 instances

## Technology Stack

- **Application**: Python 3.12, Streamlit
- **Containerization**: Docker, Docker Compose
- **Cloud Platform**: Azure App Service, Azure Container Registry
- **CI/CD**: GitHub Actions
- **Infrastructure**: Azure Bicep
- **Testing**: pytest, pytest-cov
- **Code Quality**: Ruff (linting and formatting)
- **Monitoring**: Application Insights, Log Analytics

## Documentation

- **[SETUP.md](SETUP.md)** - Complete setup guide from scratch
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Deployment verification checklist
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Common commands and operations
- **[config/README.md](config/README.md)** - Configuration documentation

## Setup and Deployment

For complete setup instructions, see [SETUP.md](SETUP.md).

Quick overview:

```bash
# 1. Deploy Azure infrastructure
./infrastructure/deploy.sh testing westeurope
./infrastructure/deploy.sh staging westeurope
./infrastructure/deploy.sh production westeurope

# 2. Configure GitHub secrets (see SETUP.md)

# 3. Deploy application
git push origin develop   # Deploys to testing
git push origin staging   # Deploys to staging
git push origin main      # Deploys to production (requires approval)
```

## Development Workflow

1. Create feature branch from `develop`
2. Make changes and add tests
3. Run tests locally: `pytest tests/ -v`
4. Commit and push
5. Create pull request to `develop`
6. CI pipeline validates changes
7. After merge, auto-deploy to testing
8. Promote through staging to production

## Monitoring and Operations

### Health Checks
```bash
# Check application health
curl https://ml-visualizer-prod.azurewebsites.net/_stcore/health
```

### View Logs
```bash
# Stream logs
az webapp log tail --name ml-visualizer-prod \
  --resource-group ml-visualizer-production-rg
```

### Scaling
```bash
# Manual scale
az appservice plan update \
  --name ml-visualizer-production-plan \
  --resource-group ml-visualizer-production-rg \
  --number-of-workers 5
```

## Configuration

Environment-specific configuration files in `/config`:
- `development.env` - Local development
- `testing.env` - Testing environment
- `staging.env` - Staging environment
- `production.env` - Production environment

See [config/README.md](config/README.md) for all available options.

## CI/CD Pipeline

### Workflows

**ci.yml** - Runs on all pushes and pull requests
- Multi-version Python testing (3.10, 3.11, 3.12)
- Linting and code formatting checks
- Security vulnerability scanning
- Docker build validation
- Test execution with coverage reporting

**deploy-testing.yml** - Deploys to testing environment
- Triggered by push to `develop` branch
- Builds and pushes Docker image to ACR
- Deploys to Azure App Service
- Runs health checks

**deploy-staging.yml** - Deploys to staging environment
- Triggered by push to `staging` branch
- Includes smoke tests
- Pre-production validation

**deploy-production.yml** - Deploys to production
- Triggered by push to `main` branch
- Requires manual approval
- Creates backup deployment slots
- Comprehensive health checks
- Supports rollback

## Security

- Non-root user in Docker containers
- Multi-stage builds for minimal attack surface
- Security scanning in CI pipeline
- HTTPS enforced in production
- Secrets managed via Azure Key Vault and GitHub Secrets
- No hardcoded credentials
- Regular dependency updates

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and add tests
4. Run tests: `pytest tests/ -v`
5. Run linting: `ruff check .`
6. Commit changes: `git commit -m 'Add new feature'`
7. Push to branch: `git push origin feature/new-feature`
8. Create Pull Request

## Troubleshooting

Common issues and solutions are documented in [SETUP.md](SETUP.md#troubleshooting).

Quick checks:
```bash
# Check Azure resources
az resource list --resource-group ml-visualizer-production-rg

# Check app service status
az webapp show --name ml-visualizer-prod \
  --resource-group ml-visualizer-production-rg --query state

# Restart application
az webapp restart --name ml-visualizer-prod \
  --resource-group ml-visualizer-production-rg
```

## License

This project is licensed under the MIT License.

## Authors

**Kofler Phillip** - HTL V - Informatik

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Deployed on [Microsoft Azure](https://azure.microsoft.com/)
- CI/CD powered by [GitHub Actions](https://github.com/features/actions)

---

**Version**: 1.0.0
**Last Updated**: December 2025
**Status**: Production Ready
