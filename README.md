# Game Project

This repository hosts the codebase for a game developed using Python with Flask/Django and MongoDB. This project is managed by a small team and aims to deliver an engaging gaming experience with a robust backend.

## Project Overview

- **Backend Framework**: Django for the server-side logic and ORM.
- **Database**: PostgreSQL for data storage and ACID transaction safety.
- **Deployment**: Docker Compose for local development and production runtime.
- **Game Logic**: Deterministic simulation service with full audit logging via StepLog.

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:

- Docker and Docker Compose
- Python 3.12 or higher (for local development outside containers)
- Git

### Quick Start with Docker Compose

The simplest way to run the application is via Docker Compose. This automatically sets up Django, PostgreSQL, and all dependencies.

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/yourgame.git
   cd yourgame
   ```

2. **Prepare Environment**

   ```bash
   cp .env.example .env
   ```

   Django management commands now load `.env` automatically when it is present.

3. **Start the Application Stack**

   **Production mode:**
   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```

   **Debug mode** (with debugpy on port 5679):
   ```bash
   docker compose -f docker/docker-compose.debug.yml up -d
   ```

4. **Access the Application**

   Open your browser and navigate to [http://localhost:8000](http://localhost:8000).

5. **Stop the Stack**

   ```bash
   docker compose -f docker/docker-compose.yml down
   # or for debug:
   docker compose -f docker/docker-compose.debug.yml down
   ```

### Local Development (Without Docker)

If you prefer to develop outside containers:

1. **Set Up Virtual Environment and Dependencies**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or: source .venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   ```bash
   cp .env.example .env
   ```

   For the default Docker setup, `.env.example` already points local Django at PostgreSQL on `localhost:5433`, and `manage.py` will load `.env` automatically.
   If you are running PostgreSQL separately, update `.env` to match your own host, port, and credentials.

3. **Run Migrations**

   ```bash
   python manage.py migrate
   ```

4. **Start the Development Server**

   ```bash
   python manage.py runserver
   ```

   The app will be available at [http://localhost:8000](http://localhost:8000).

## Development Guidelines

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- Use meaningful commit messages to describe your changes.

### Branching Strategy

- Use `main` for stable code.
- Create feature branches for new functionality (`feature/feature-name`).
- Submit a pull request for code review before merging.

### Testing

Tests are located in the `tests/` directory. To run tests:

**With Docker:**
```bash
docker compose -f docker/docker-compose.yml exec web python manage.py test
```

**Locally:**
```bash
python manage.py test
```

If you are using Docker for PostgreSQL and running Django from the host, start the stack first so the database is listening on `localhost:5433`:

```bash
docker compose -f docker/docker-compose.yml up -d db
python manage.py test
```

Ensure all tests pass before submitting a pull request.

### Security Scanning (Snyk)

You can run Snyk checks locally (Windows PowerShell) using Docker:

1. Create a Snyk account and API token.
2. Set your token in the current shell:

   ```powershell
   $env:SNYK_TOKEN="your-token"
   ```

3. Run the scanner script:

   ```powershell
   .\scripts\snyk_scan.ps1
   ```

   Optional severity threshold:

   ```powershell
   .\scripts\snyk_scan.ps1 -SeverityThreshold medium
   ```

CI also runs dependency and code scans via `.github/workflows/snyk.yml` when `SNYK_TOKEN` is configured in repository secrets.

## Security

Please refer to our [SECURITY.md](SECURITY.md) file for information on how to report vulnerabilities and security concerns.

## Contributing

We welcome contributions! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for more information on how to get started.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any queries or issues, please contact the project maintainer:

**Kristian Peacocke**  
[krpeacocke@gmail.com](mailto:krpeacocke@gmail.com)
