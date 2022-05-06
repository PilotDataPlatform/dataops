# DataOps Utility Service

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
