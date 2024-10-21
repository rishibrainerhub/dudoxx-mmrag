# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app
VOLUME /app
ENV PATH=/app/.venv/bin:$PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install pipenv
ENV PATH=/root/.local/bin:$PATH
ENV PIPENV_VENV_IN_PROJECT=true
RUN pip install --user pipenv

# Expose the port that FastAPI will run on
EXPOSE 8000

ENTRYPOINT ["/bin/sh", "-eu", "/app/dev.sh"]