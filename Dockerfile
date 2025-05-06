FROM python:3.12
LABEL maintainer="iscenkoa@gmail.com"

# Setting environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=off

# Installing dependencies
RUN apt update && apt install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    postgresql-client \
    dos2unix \
    && apt clean

# Install Poetry
RUN python -m pip install --upgrade pip && \
    pip install poetry

# Copy dependency files
COPY ./poetry.lock /usr/src/poetry/poetry.lock
COPY ./pyproject.toml /usr/src/poetry/pyproject.toml

# Configure Poetry to avoid creating a virtual environment
RUN poetry config virtualenvs.create false

# Selecting a working directory
WORKDIR /usr/src/poetry

# Install dependencies with Poetry
# RUN poetry lock
RUN poetry install --no-root --only main

# Selecting a working directory
WORKDIR /usr/src/django

# Copy the source code
COPY . .

# Copy commands
# COPY ./commands /commands

# # Ensure Unix-style line endings for scripts
# RUN dos2unix /commands/*.sh

# # Add execute bit to commands files
# RUN chmod +x /commands/*.sh
CMD ["gunicorn", "spa.wsgi:application", "--bind", "0.0.0.0:8000"]
