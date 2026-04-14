FROM python:3.11-slim

WORKDIR /usr/src/app

# Install dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* /usr/src/app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY . /usr/src/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
