# DUDOXX-MMRAG

## Project Overview

DUDOXX-MMRAG is an advanced, AI-powered API designed to support healthcare professionals in accessing comprehensive, up-to-date medical information. This project leverages FastAPI for the backend, incorporates multi-modal input processing, and utilizes retrieval-augmented generation (RAG) to provide accurate and context-aware responses.

## Key Features

- **FastAPI-based REST Server**: High-performance backend built with FastAPI
- **Modern Frontend**: Responsive UI built with HTML, CSS, and JavaScript
- **Multi-modal Input Processing**: Capable of handling various input types
- **Retrieval-Augmented Generation (RAG)**: Enhances response accuracy with contextual information
- **AI Integration**: Leverages OpenAI's powerful language models
- **Web Search Capability**: Integrates DuckDuckGo for up-to-date information retrieval
- **Secure Access Management**: Ensures data protection and user authentication
- **Docker Support**: Easy deployment and scalability with Docker and Docker Compose

## Prerequisites

- Docker
- Docker Compose
- Make (optional, for using Makefile commands)

## Getting Started

1. Clone the repository:
   ```
   git clone https://github.com/your-username/DUDOXX-MMRAG.git
   cd DUDOXX-MMRAG
   ```

2. Set up environment variables:
   ```
   cd backend
   cp .env.template .env
   ```
   Edit the `.env` file with your specific configuration.

3. Build and run the project:
   ```
   make run
   ```
This will only start the backend to start the full application use the main docker file

## Docker Compose Configuration

The project uses `docker-compose.yml` to orchestrate all services:
- Backend (FastAPI)
- Frontend (HTML/CSS/JavaScript)
- Redis (for caching and session management)

## Makefile Commands

For ease of use, a Makefile is provided with the following commands:

- `make ps`: List running Docker containers
- `make build`: Build the Docker images
- `make up`: Start all containers
- `make down` or `make d`: Stop and remove all containers
- `make run` or `make r`: Build and start the project (shortcut for `build` and `up`)

## Accessing the Application

- Frontend: http://localhost:8080
- Backend Swagger UI: http://localhost:8000/docs

## Development

To contribute to the project:

1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Submit a pull request

