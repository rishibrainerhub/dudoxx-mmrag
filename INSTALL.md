# Installation Guide for DUDOXX-MMRAG

This guide provides step-by-step instructions for installing and setting up the DUDOXX-MMRAG project.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Docker (version 20.10 or later)
- Docker Compose (version 1.29 or later)
- Git
- Make (optional, but recommended for using Makefile commands)

## Installation Steps

1. **Clone the Repository**

   Open a terminal and run:
   ```
   git clone https://github.com/rishibrainerhub/dudoxx-mmrag
   cd dudoxx-mmrag
   ```

2. **Set Up Environment Variables**

   Navigate to the backend directory and create a `.env` file:
   ```
   cd backend
   cp .env.template .env
   ```
   
   Open the `.env` file in a text editor and fill in the required values:
   ```
   OPENAI_API_KEY=""
   DDX_MMRAG_REDIS_HOST=''
   DDX_MMRAG_REDIS_PORT=
   DDX_MMRAG_SQLITE_DB=''
   # Add any other required environment variables
   ```

3. **Build Docker Images**

   Return to the project root directory and build the Docker images:
   ```
   cd ..
   make build
   ```

   If you don't have Make installed, you can use the Docker Compose command directly:
   ```
   docker-compose build
   ```

4. **Start the Services**

   Start all the services using:
   ```
   make up
   ```
   
   Or without Make:
   ```
   docker-compose up -d
   ```

5. **Verify Installation**

   Check if all services are running:
   ```
   make ps
   ```
   
   Or without Make:
   ```
   docker-compose ps
   ```

   You should see containers for the backend, frontend, and Redis running.

## Troubleshooting

If you encounter any issues during installation:

1. Ensure all ports required by the application (8000 for backend, 8080 for frontend) are available and not in use by other applications.

2. Check Docker logs for any error messages:
   ```
   docker-compose logs
   ```

3. Verify that all environment variables in the `.env` file are correctly set.

4. If you're behind a corporate firewall, ensure that Docker has the necessary permissions to pull images and access required URLs.

5. For any persistent issues, please refer to the project's GitHub issues page or contact the maintainers.

## Updating

To update the project to the latest version:

1. Pull the latest changes:
   ```
   git pull origin main
   ```

2. Rebuild the Docker images:
   ```
   make build
   ```

3. Restart the services:
   ```
   make down
   make up
   ```

For more detailed usage instructions, please refer to the USAGE.md file.