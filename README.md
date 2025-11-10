# ProDvor Backend

This is the backend for the ProDvor project, a platform for sports enthusiasts. It is built with Python and the FastAPI framework, providing a robust and scalable API for the frontend application.

## Tech Stack

*   **Framework**: FastAPI
*   **Database**: PostgreSQL with SQLAlchemy ORM
*   **Asynchronous Server Gateway Interface (ASGI)**: Uvicorn
*   **Web Server Gateway Interface (WSGI) HTTP Server**: Gunicorn
*   **Containerization**: Docker
*   **Dependency Management**: pip and `requirements.txt`
*   **Code Quality**: `structlog` for structured logging.

## Project Structure

```
├── app/
│   ├── core/
│   │   ├── config.py       # Pydantic settings management
│   │   ├── logging.py      # Logging configuration
│   │   └── security.py     # Password hashing and token generation
│   ├── crud/             # Create, Read, Update, Delete database operations
│   ├── models/           # SQLAlchemy database models
│   ├── schemas/          # Pydantic data validation schemas
│   ├── routers/          # API endpoint definitions (auth, users, etc.)
│   └── dependencies.py   # FastAPI dependencies
├── .github/workflows/
│   └── ci.yml            # GitHub Actions CI configuration
├── .env.example          # Example environment variables
├── main.py               # Main FastAPI application entrypoint
├── Dockerfile            # Docker configuration for production
├── gunicorn.conf.py      # Gunicorn server configuration
└── requirements.txt      # Python dependencies
```

## Getting Started

### Prerequisites

*   Python 3.11+
*   Docker and Docker Compose
*   An accessible PostgreSQL database

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    Create a `.env` file in the project root by copying the example file, and fill in the required values (especially for the database connection).
    ```bash
    cp .env.example .env
    # Now edit .env with your configuration
    ```

### Running the Application

**For Development:**

Run the application using Uvicorn. The `--reload` flag will automatically restart the server on code changes.

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

**For Production (with Docker):**

1.  **Build the Docker image:**
    ```bash
    docker build -t prodvor-backend .
    ```

2.  **Run the container:**
    Make sure your `.env` file is present and configured.
    ```bash
    docker run -p 8000:8000 --env-file .env prodvor-backend
    ```

## API Endpoints

The API is structured using FastAPI routers. The main endpoints are:

*   `/api/v1/auth/`: User registration, login, logout, and token refresh.
*   `/api/v1/users/`: User management.
*   `/api/v1/subscriptions/`: Subscription management.
*   `/healthz`: Health check endpoint.

For a detailed and interactive API documentation, run the application and visit `http://localhost:8000/docs`.

## Continuous Integration

This project uses GitHub Actions for Continuous Integration. The workflow, defined in `.github/workflows/ci.yml`, automatically builds the Docker image on every push to the `main` branch to ensure that the application is always in a deployable state.
