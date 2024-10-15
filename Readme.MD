# DUDOXX-MMRAG# DUDOXX-MMRAG

## Project Overview

The DUDOXX-MMRAG project is an advanced, AI-powered API designed to support healthcare professionals in accessing comprehensive, up-to-date medical information. This FastAPI-based REST server incorporates multi-modal input processing, retrieval-augmented generation (RAG), and secure access management.

## Features

- FastAPI-based REST server
- Multi-modal input processing
- Retrieval-augmented generation (RAG)
- Integration with OpenAI and DuckDuckGo
- Secure access management

## Docker Compose

The project includes two Docker Compose files:

1. `docker-compose-backend.yml`: For running the main project
2. `docker-compose-backend-test.yml`: For running test cases

## Makefile

A Makefile is provided to simplify common tasks and ensure cross-platform compatibility. It detects the operating system and uses appropriate commands for Linux (Ubuntu) and Windows.

### Available Commands

- `make ps`: List running Docker containers
- `make build`: Build the main project Docker image
- `make up`: Start the main project containers
- `make down` or `make d`: Stop and remove the main project containers
- `make test-build`: Build the test Docker image
- `make test-up`: Run the test containers
- `make run` or `make r`: Build and start the main project (shortcut for `build` and `up`)
- `make test` or `make t`: Build and run tests (shortcut for `test-build` and `test-up`)

## Getting Started

1. Clone the repository
2. Install Docker and Docker Compose
3. Use the provided Makefile commands to build and run the project

For example, to start the main backend:

Go to the backend directory

```bash
cd backend
```
then 
```bash
make run
```

To run tests:

```bash
make test
```

To stop

```bash
make down
```