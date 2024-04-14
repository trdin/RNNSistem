# Use the official Python image as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    FLASK_APP="src.serve.serve:main"

# Install system dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Copy only dependencies to leverage Docker cache
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Install project dependencies
RUN poetry install --no-interaction

# Copy the rest of the code
COPY . /code

# Expose the port the app runs on
EXPOSE 3001

# Command to run the application
CMD ["poetry", "run", "serve"]
