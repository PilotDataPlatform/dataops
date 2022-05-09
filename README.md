# DataOps Utility Service
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.7](https://img.shields.io/badge/python-3.7-green?style=for-the-badge)](https://www.python.org/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/PilotDataPlatform/dataops/CI/develop?style=for-the-badge)](https://github.com/PilotDataPlatform/dataops/actions/workflows/cicd.yml)

[![codecov](https://img.shields.io/codecov/c/github/PilotDataPlatform/dataops?style=for-the-badge)](https://codecov.io/gh/PilotDataPlatform/dataops)

## About
This service contains dataops that should not have access to greenroom. It's built using the FastAPI python framework.

### Prerequisites
- [Poetry](https://python-poetry.org/) dependency manager.

### Installation
1. Install [Poetry](https://python-poetry.org/docs/#installation).
2. Configure access to internal package registry.

       poetry config http-basic.pilot ${PIP_USERNAME} ${PIP_PASSWORD}

3. Install dependencies.

       poetry install

4. Add environment variables into `.env`.
5. Run application.

       poetry run python start.py

### Docker

*docker-compose*

`docker-compose build`
`docker-compose up`

*Plain old docker*

`docker build . -t service_data_ops`
`docker run service_data_ops`
