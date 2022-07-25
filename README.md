# DataOps Utility Service
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9](https://img.shields.io/badge/python-3.9-green?style=for-the-badge)](https://www.python.org/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/PilotDataPlatform/dataops/CI/develop?style=for-the-badge)](https://github.com/PilotDataPlatform/dataops/actions/workflows/cicd.yml)
[![codecov](https://img.shields.io/codecov/c/github/PilotDataPlatform/dataops?style=for-the-badge)](https://codecov.io/gh/PilotDataPlatform/dataops)

Manages file/folder operations (copy, delete). This is accomplished by dispatching operation requests received by the portal to the Queue service and managing the status of each respective copy/delete process in Redis. In addition, the generation and retrieval of previews of zipped files are managed in this service.


## Getting Started

To get a local copy of the service up and running follow these simple example steps.


### Prerequisites

This project is using [Poetry](https://python-poetry.org/docs/#installation) to handle the dependencies.

    curl -sSL https://install.python-poetry.org | python3 -

### Installation & Quick Start

1. Clone the project.

       git clone https://github.com/PilotDataPlatform/dataops.git

2. Install dependencies.

       poetry install

3. Run setup script for creating PostgreSQL database (schema created during Alembic migration).

       - [Create Database](https://github.com/PilotDataPlatform/dataops/blob/develop/migrations/scripts/create_db.sql)

5. Add environment variables into `.env` in case it's needed. Use `.env.schema` as a reference.


6. Run any initial scripts, migrations or database seeders.

       poetry run alembic upgrade head

7. Run application.

       poetry run python start.py

### Startup using Docker

This project can also be started using [Docker](https://www.docker.com/get-started/).

1. To build and start the service within the Docker container, run:

       docker compose up

2. Migrations should run automatically after the previous step. They can also be manually triggered:

       docker compose run --rm alembic upgrade head

## Resources

* [Pilot Platform API Documentation](https://pilotdataplatform.github.io/api-docs/)
* [Pilot Platform Helm Charts](https://github.com/PilotDataPlatform/helm-charts/)

## Contribution

You can contribute the project in following ways:

* Report a bug.
* Suggest a feature.
* Open a pull request for fixing issues or adding functionality. Please consider
  using [pre-commit](https://pre-commit.com) in this case.
* For general guidelines on how to contribute to the project, please take a look at the [contribution guides](CONTRIBUTING.md).

