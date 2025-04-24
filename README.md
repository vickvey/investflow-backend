# Investflow Backend

Investflow Backend is a FastAPI-based API server for the Investflow application, providing endpoints for stock-related operations, portfolio optimization, and integrating with a frontend that uses Clerk for authentication. This document outlines the project structure, setup instructions, and guidelines for contributing.

## Table of Contents
- [Project Overview](#project-overview)
- [Directory Structure](#directory-structure)
- [Setup Instructions](#setup-instructions)
- [Authentication](#authentication)
- [Contributing](#contributing)
- [Running Tests](#running-tests)

## Project Overview
The Investflow Backend serves as the API layer for the Investflow application, handling stock-related data, portfolio optimization, and risk calculations. It is built with FastAPI for high performance and integrates with a frontend that uses Clerk for user authentication. The backend verifies JWTs issued by Clerk to secure protected endpoints.

## Directory Structure
The project is organized as follows:

```
investflow-backend/
├── src/
│   ├── dependencies.py          # FastAPI dependencies (e.g., JWT validation, database sessions)
│   ├── internal/
│   │   ├── __init__.py
│   │   ├── admin_routes.py     # Admin-specific API endpoints
│   │   └── admin_services.py   # Admin-specific business logic
│   ├── main.py                 # FastAPI application entry point
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── optimizer_routes.py # API endpoints for portfolio optimization
│   │   └── stock_routes.py     # API endpoints for stock-related operations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_fetcher.py     # Logic for fetching stock data
│   │   ├── optimizers/
│   │   │   ├── black_litterman.py       # Black-Litterman optimization model
│   │   │   ├── maximum_sharpe_ratio.py  # Maximum Sharpe Ratio optimization
│   │   │   ├── mean_variance.py         # Mean-Variance optimization
│   │   │   ├── minimum_variance_optimizer.py # Minimum Variance optimization
│   │   │   └── risk_parity.py           # Risk Parity optimization
│   │   ├── return_models/
│   │   │   ├── capm.py                 # CAPM return model
│   │   │   ├── equal_weighted.py        # Equal-weighted return model
│   │   │   ├── factor_model.py          # Factor-based return model
│   │   │   └── historical_return.py     # Historical return model
│   │   ├── risk_calculator.py          # Risk calculation logic
│   │   └── stock_service.py            # Business logic for stock-related operations
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_stock_routes.py        # Unit and integration tests for stock endpoints
│   ├── utils/
│   │   ├── __init__.py
│   │   └── some_util.py               # Utility functions (e.g., helper methods, logging)
│   └── __pycache__/                   # Compiled Python files (auto-generated)
├── tests/
│   ├── __init__.py
│   └── test_stock_routes.py           # Unit and integration tests for stock endpoints
├── .env                               # Environment variables (not tracked in git)
├── .env.example                       # Example environment variables for setup
├── Dockerfile                         # Docker configuration for containerized deployment
├── docker-compose.yml                 # Docker Compose for local development
├── requirements.txt                   # Project dependencies
├── alembic/                           # Database migrations (if using SQLAlchemy)
│   ├── env.py
│   └── script.py.migrations
├── alembic.ini                        # Alembic configuration for migrations
└── README.md                          # Project documentation (this file)
```

### Purpose of Key Files and Folders
- **`src/`**: Contains the core application code.
  - **`dependencies.py`**: Defines FastAPI dependencies for reusable logic (e.g., JWT validation, database sessions).
  - **`internal/`**:
    - **`admin_routes.py`**: Defines admin-specific API endpoints.
    - **`admin_services.py`**: Implements admin-specific business logic.
  - **`main.py`**: Initializes the FastAPI app and mounts routers.
  - **`routers/`**:
    - **`optimizer_routes.py`**: Defines API endpoints for portfolio optimization (e.g., Black-Litterman, Mean-Variance).
    - **`stock_routes.py`**: Defines API endpoints for stock-related operations (e.g., GET /stocks, POST /stocks).
  - **`services/`**:
    - **`data_fetcher.py`**: Handles fetching stock data from external sources.
    - **`optimizers/`**: Contains portfolio optimization models (e.g., Black-Litterman, Maximum Sharpe Ratio).
    - **`return_models/`**: Implements return calculation models (e.g., CAPM, Historical Returns).
    - **`risk_calculator.py`**: Provides logic for calculating portfolio risk.
    - **`stock_service.py`**: Implements business logic for stock-related operations.
  - **`tests/`**: Contains unit and integration tests for stock endpoints.
  - **`utils/some_util.py`**: Houses utility functions (e.g., logging, data formatting).
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
- **JWT Validation**: Implemented using Clerk's JWKS endpoint.
- **Dependencies**: Defined in `dependencies.py` for reusable token validation.
- **Configuration**: Clerk's JWKS URL and other settings are stored in environment variables.

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