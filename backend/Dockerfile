# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app
VOLUME /app
ENV PATH=/app/.venv/bin:$PATH

# install & configure pipenv for a local development environment
ENV PATH=/root/.local/bin:$PATH
ENV PIPENV_VENV_IN_PROJECT=true
RUN pip install --user pipenv
RUN apt update && apt install -y build-essential libpq-dev

# Expose the port that FastAPI will run on
EXPOSE 8000

ENTRYPOINT ["/bin/sh", "-eu", "/app/dev.sh"]
