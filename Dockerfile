FROM python:3.11-slim

WORKDIR /usr/src/app

# Ensure application package is importable
ENV PYTHONPATH=/usr/src/app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev default-libmysqlclient-dev \
    ca-certificates wget gnupg unzip \
    # libraries required by Chromium and Chrome
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 libxcomposite1 libxrandr2 libxss1 libgtk-3-0 \
    fonts-liberation libasound2 libpangocairo-1.0-0 libdbus-1-3 \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install --no-cache-dir poetry

COPY . /usr/src/app

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Install Selenium runtime Python packages not managed by poetry (webdriver-manager)
RUN pip install --no-cache-dir selenium webdriver-manager pydantic-settings \
    fastapi uvicorn sqlalchemy asyncmy pydantic alembic aiosqlite passlib[bcrypt] python-jose python-dotenv httpx python-multipart

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
