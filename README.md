# Investflow Backend

Investflow Backend is a FastAPI-based API server for the Investflow application, providing endpoints for stock-related operations and integrating with a frontend that uses Clerk for authentication. This document outlines the project structure, setup instructions, and guidelines for contributing.

## Table of Contents
- [Project Overview](#project-overview)
- [Directory Structure](#directory-structure)
- [Setup Instructions](#setup-instructions)
- [Authentication](#authentication)
- [Contributing](#contributing)
- [Running Tests](#running-tests)

## Project Overview
The Investflow Backend serves as the API layer for the Investflow application, handling stock-related data and operations. It is built with FastAPI for high performance and integrates with a frontend that uses Clerk for user authentication. The backend verifies JWTs issued by Clerk to secure protected endpoints.

## Directory Structure
The project is organized as follows:

```
investflow-backend/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py           # Environment variables and configuration (e.g., Clerk JWKS URL, database settings)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py            # Database models (e.g., SQLAlchemy ORM models)
│   │   └── connections.py       # Database connection setup and configuration
│   ├── dependencies.py          # FastAPI dependencies (e.g., JWT validation, database sessions)
│   ├── internal/
│   │   ├── __init__.py
│   │   └── admin.py            # Admin-specific logic (e.g., admin routes or services)
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py             # Middleware for Clerk JWT validation
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models for API request/response validation
│   ├── routers/
│   │   ├── __init__.py
│   │   └── stocks.py           # API endpoints for stock-related operations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py             # Logic for verifying Clerk JWTs
│   │   └── stocks.py           # Business logic for stock-related operations
│   ├── utils/
│   │   ├── __init__.py
│   │   └── some_util.py        # Utility functions (e.g., helper methods, logging)
│   ├── main.py                 # FastAPI application entry point
│   └── __pycache__/            # Compiled Python files (auto-generated)
├── tests/
│   ├── __init__.py
│   │   └── test_stocks.py      # Unit and integration tests for stock endpoints
├── .env                        # Environment variables (not tracked in git)
├── .env.example                # Example environment variables for setup
├── Dockerfile                  # Docker configuration for containerized deployment
├── docker-compose.yml          # Docker Compose for local development
├── requirements.txt            # Project dependencies
├── alembic/                    # Database migrations (if using SQLAlchemy)
│   ├── env.py
│   └── script.py.migrations
├── alembic.ini                 # Alembic configuration for migrations
└── README.md                   # Project documentation (this file)
```

### Purpose of Key Files and Folders
- **`src/`**: Contains the core application code.
  - **`config/settings.py`**: Loads environment variables (e.g., Clerk JWKS URL, database URL) using `python-dotenv`.
  - **`database/`**: Manages database models and connections (e.g., SQLAlchemy models, connection pooling).
  - **`dependencies.py`**: Defines FastAPI dependencies for reusable logic (e.g., JWT validation, database sessions).
  - **`internal/admin.py`**: Handles admin-specific functionality (e.g., admin routes or services; consider renaming for clarity).
  - **`middleware/auth.py`**: Implements middleware to validate Clerk JWTs for protected routes.
  - **`models/schemas.py`**: Defines Pydantic models for API request/response validation.
  - **`routers/stocks.py`**: Defines API endpoints for stock-related operations (e.g., GET /stocks, POST /stocks).
  - **`services/auth.py`**: Contains logic for verifying Clerk JWTs.
  - **`services/stocks.py`**: Implements business logic for stock-related operations.
  - **`utils/some_util.py`**: Houses utility functions (e.g., logging, data formatting).
  - **`main.py`**: Initializes the FastAPI app and mounts routers.
- **`tests/`**: Contains unit and integration tests for the application.
- **`.env`**: Stores sensitive environment variables (e.g., Clerk JWKS URL, database credentials).
- **`.env.example`**: Provides a template for environment variables.
- **`Dockerfile`**: Defines the Docker image for the application.
- **`docker-compose.yml`**: Configures services for local development (e.g., API, database).
- **`requirements.txt`**: Lists Python dependencies.
- **`alembic/`**: Manages database migrations (if using SQLAlchemy).

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd investflow-backend
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update `.env` with your configuration (e.g., Clerk JWKS URL, database URL).

5. **Set Up Database** (if applicable):
   - Initialize the database using your ORM (e.g., SQLAlchemy).
   - Run migrations (if using Alembic):
     ```bash
     alembic upgrade head
     ```

6. **Run the Application**:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```
   - Access the API at `http://localhost:8000`.
   - View API documentation at `http://localhost:8000/docs`.

7. **Run with Docker** (optional):
   ```bash
   docker-compose up --build
   ```

## Authentication
The frontend uses Clerk for user authentication, which issues JWTs. The backend verifies these JWTs to secure protected endpoints:
- **JWT Validation**: Implemented in `middleware/auth.py` using Clerk's JWKS endpoint.
- **Dependencies**: Defined in `dependencies.py` for reusable token validation.
- **Configuration**: Clerk's JWKS URL and other settings are stored in `config/settings.py`.

To add a protected endpoint:
1. Use the `Depends` function in `dependencies.py` to validate JWTs.
2. Apply the dependency to your route in `routers/`.

## Contributing
- Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages.
- Write tests for new features in the `tests/` directory.
- Update API documentation in endpoint descriptions (visible in `/docs`).
- Ensure code passes linting and tests before submitting a pull request:
  ```bash
  pytest tests/
  ```

## Running Tests
Run unit and integration tests using pytest:
```bash
pytest tests/
```

For coverage reports:
```bash
pytest --cov=src tests/
```

---

This project is under active development. Feel free to raise issues or submit pull requests to improve the backend!