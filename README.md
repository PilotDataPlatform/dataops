# DataOps Utility Service
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9](https://img.shields.io/badge/python-3.9-green?style=for-the-badge)](https://www.python.org/)
[![GitHub Workflow Status (branch)](https://img.shields.io/github/workflow/status/PilotDataPlatform/dataops/CI/develop?style=for-the-badge)](https://github.com/PilotDataPlatform/dataops/actions/workflows/cicd.yml)
[![codecov](https://img.shields.io/codecov/c/github/PilotDataPlatform/dataops?style=for-the-badge)](https://codecov.io/gh/PilotDataPlatform/dataops)

Service Description

Manages file/folder operations (copy, delete). This is accomplished by dispatching operation requests received by 
the portal to the Queue service and managing the status of each respective copy/delete process in Redis. In addition,
the generation and retrieval of previews of zipped files are managed in this service.

## Built With
 - [fastapi](https://fastapi.tiangolo.com): The async api framework for backend

 - [poetry](https://python-poetry.org/): python package management

 - [docker](https://docker.com): Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers

## Getting Started

To get a local copy up and running follow these simple example steps.

### Prerequisites

 1. The project is using poetry to handle the package. **Note here the poetry must install globally not in the anaconda virtual environment**

 ```
 pip install poetry
 ```

 2. Add the precommit package:

 ```
 pip install pre_commit
 ```

### Installation

 1. git clone the project:
 ```
 git clone https://github.com/PilotDataPlatform/sandbox.git
 ```

 2. install the package:
 ```
 poetry install
 ```

 3. create the `.env` file from `.env.schema`




 4. perform Alembic schema upgrade:
 ```
 poetry run alembic upgrade head
 ```
 5. perform Alembic schema revision if you change model schema (optional):
 ```
 poetry run alembic revision --autogenerate -m "Migration message"
 ```
 6. run it locally:
 ```
 poetry run python start.py
 ```

### Testing

```
poetry run pytest -c tests/pytest.ini
```

### Dockerizing

To wrap up the service into a docker container, run following command:

```
docker-compose build
docker-compose up
```
To run an Alembic schema revision:
```
docker compose run --rm alembic revision --autogenerate -m "Migration message"
```

## Resources

* [API Document](https://pilotdataplatform.github.io/api-docs/) 
* [Helm Chart](https://github.com/PilotDataPlatform/helm-charts/)

## Contribution

You can contribute the project in following ways:

* Report a bug
* Suggest a feature
* Open a pull request for fixing issues or developing plugins