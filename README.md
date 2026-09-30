# Quest Between

Quest Between is a browser-based, single-player campaign game built with Django and PostgreSQL. Players manage a party between simulated expeditions through travel, settlement actions, events, trade, healing, and progression.

Expeditions resolve off-screen. Dungeon maps, tactical combat, and multiplayer are outside the current product scope.

## Project Overview

- **Backend**: Django with a service layer for campaign rules.
- **Database**: PostgreSQL for persistent campaign state and transactions.
- **Interface**: Server-rendered Django templates with HTMX.
- **Deployment**: Docker Compose for self-hosted installations.
- **Simulation**: Seeded outcomes with campaign StepLogs for auditability.

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:

- Docker and Docker Compose
- Python 3.12 or higher (for local development outside containers)
- Git

### Quick Start with Docker Compose

The simplest way to run the application is via Docker Compose. This automatically sets up Django, PostgreSQL, and all dependencies.

1. **Get the repository**

   Check out this repository using its configured Git remote, then open the project directory.

2. **Prepare Environment**

   ```bash
   cp .env.example .env
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

   Put the generated value in `DJANGO_SECRET_KEY` and choose a strong
   `POSTGRES_PASSWORD`. Set `DJANGO_ALLOWED_HOSTS` to the hostnames or IP
   addresses players will use. Keep `.env` local and untracked.

3. **Start the Application Stack**

   **Production mode:**

   ```bash
   docker compose -f docker/docker-compose.yml up -d
   ```

   Put the production stack behind a TLS-terminating reverse proxy and configure
   it to forward `X-Forwarded-Proto`. The Django production settings redirect
   HTTP to HTTPS and use secure cookies.

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
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**

   ```bash
   cp .env.example .env
   ```

   If you are running PostgreSQL separately for host-side development, update `.env` to match your own host, port, and credentials.

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

Check Python code with Ruff:

```bash
python -m ruff check .
python -m ruff format --check .
python -m mypy
```

Run `python -m ruff format .` to apply formatting.

### Branching Strategy

- Use `main` for stable code.
- Create feature branches for new functionality (`feature/feature-name`).
- Submit a pull request for code review before merging.

### Testing

Tests are located in the `tests/` directory. To run tests:

**With Docker:**

```bash
docker compose -f docker/docker-compose.yml exec web python manage.py test campaign
```

**Locally:**

```bash
python manage.py test campaign
```

For a Docker-independent host-side test run, use the dedicated SQLite-backed settings profile:

```bash
python manage.py test campaign --settings=questbetween.settings_test
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
