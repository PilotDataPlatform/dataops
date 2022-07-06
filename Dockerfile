# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not, see http://www.gnu.org/licenses/.

FROM python:3.9-buster AS production-environment

ARG PIP_USERNAME
ARG PIP_PASSWORD

WORKDIR /usr/src/app
ENV TZ=America/Toronto

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get update && \
    apt-get install -y vim-tiny less && \
    ln -s /usr/bin/vim.tiny /usr/bin/vim && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry==1.1.12
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root --no-interaction

FROM production-environment AS dataops-image

COPY . .
RUN chmod +x gunicorn_starter.sh
CMD ["./gunicorn_starter.sh"]

FROM production-environment AS development-environment

RUN poetry install --no-root --no-interaction

FROM development-environment AS alembic-image

ENV ALEMBIC_CONFIG=migrations/alembic.ini

COPY . .
ENTRYPOINT ["python3", "-m", "alembic"]

CMD ["upgrade", "head"]
