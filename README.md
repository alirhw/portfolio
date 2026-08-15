# Portfolio

Personal Developer Portfolio built with Django.

This project is implemented as a modular Django monolith with server-side rendered templates.

---

## Current Status

The project is currently in the foundation stage (**Phase 01 - Milestone M0**).

### Completed:
- Django project foundation and directory structure
- Environment-separated settings (`base.py`, `development.py`, `test.py`, `production.py`)
- Fail-closed security architecture for production
- Static and media configuration with source vs collected output separation
- WhiteNoise production static file handling
- Minimal server-rendered home page (`base.html`)
- UV dependency management and pyproject tooling (`Ruff`, `pytest`)
- Foundation documentation and clean-environment validation

*Domain models and business functionality are not implemented yet.*

---

## Tech Stack

- **Python**: `>=3.14,<3.15` (CPython 3.14.x)
- **Framework**: Django `6.1.x`
- **Database**: PostgreSQL (planned for production runtime; SQLite used for local foundation)
- **Dependency & Environment Manager**: `uv`
- **Linter & Formatter**: Ruff
- **Test Runner**: Pytest + pytest-django (configuration baseline initialized)
- **Static Assets**: WhiteNoise + Django Staticfiles
- **Templates**: Django Templates (Server-Side Rendered)

*Note: Some tools and packages are introduced in upcoming phases and are not yet active in the current foundation stage.*

---

## Prerequisites

Before starting, make sure you have installed:

- **Python 3.14.x**
- **uv** (>= 0.12.x)
- **Git**

---

## Getting the Project

Clone the repository:

```bash
git clone <repository-url>
cd portfolio
```

---

## Installing Dependencies

Synchronize the virtual environment using `uv`:

```bash
uv sync
```

This command creates a local `.venv` and installs exact dependency versions resolved in `uv.lock`.

---

## Environment Variables

Create a local `.env` file from `.env.example`:

**Linux / macOS:**
```bash
cp .env.example .env
```

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

> **IMPORTANT**: The `.env` file contains sensitive local settings and must **never** be committed to Git. It is automatically ignored in `.gitignore`.

### Documented Variables (1:1 with `.env.example`):

1. `DJANGO_SECRET_KEY`
   - Secret key used for cryptographic signing.
   - For local development, a placeholder/development-only value can be used.
   - Production **fails closed** (raises `KeyError` and halts startup) if this variable is not provided.

2. `DJANGO_ALLOWED_HOSTS`
   - Comma-separated list of host/domain names that this Django site can serve.
   - Example: `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`
   - Production requires this variable and fails closed if missing.

3. `DJANGO_CSRF_TRUSTED_ORIGINS`
   - Comma-separated list of trusted origins for unsafe requests (e.g. POST) under CSRF protection.
   - Example: `DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000`
   - Production requires this variable and fails closed if missing.

---

## Local Development

The default settings module for local operations is `config.settings.development`.

1. **Run Django System Checks:**
   ```bash
   uv run manage.py check
   ```

2. **Start the Development Server:**
   ```bash
   uv run manage.py runserver
   ```

3. **Open in Browser:**
   Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to see the minimal foundation page.

---

## Settings Architecture

Settings are split cleanly by environment under `config/settings/`:

```text
config/settings/
├── __init__.py
├── base.py
├── development.py
├── test.py
└── production.py
```

- **`base.py`**: Common settings shared across all environments (installed apps, middleware, template engine, internationalization, static/media path configurations).
- **`development.py`**: Local developer settings (`DEBUG = True`, console email backend, local memory cache, permissive local defaults).
- **`test.py`**: Isolated test environment settings (`DEBUG = False`, locmem email backend, isolated cache).
- **`production.py`**: Strict production settings (`DEBUG = False` hardcoded, fail-closed environment variables, WhiteNoise storage, secure cookies, and full HTTPS redirect/HSTS headers).

---

## Static and Media Files

The project strictly separates source static files, collected deployment artifacts, and user-uploaded media:

- **Source Static Files (`static/`)**: Located in `static/` and referenced via `STATICFILES_DIRS`.
- **Collected Static Files (`staticfiles/`)**: Output destination for `collectstatic`, served via WhiteNoise in production.
- **Media Files (`media/`)**: Target directory for user/admin media files (`MEDIA_ROOT`).

### Validating Static Assets:

- **Find a static file in source directories:**
  ```bash
  uv run manage.py findstatic css/base.css
  ```

- **Collect static files for production:**
  ```bash
  uv run manage.py collectstatic --noinput
  ```

---

## Testing & Quality Assurance

- **Code Linting (Ruff):**
  ```bash
  uv run ruff check --no-fix
  ```

- **Pytest Configuration Verification:**
  ```bash
  uv run pytest --collect-only
  ```

*Note: The comprehensive automated test suite will be implemented in Phase 02 (T-008).*

---

## What Is Not Implemented Yet (Intentionally Deferred)

The presence of architectural directories does not imply feature completion. The following features belong to later phases:

- Domain models and migrations (`Project`, `Experience`, `Education`, `Skill`, `Message`)
- Portfolio administration interface
- Contact form processing & email dispatch
- GitHub API background sync integration
- Interactive retro terminal UI
- Redis & Celery background task processing
- Docker containerization & production deployment manifests
- CI/CD automated workflow pipeline
- Multi-language & RTL switcher

---

## Foundation Validation Checklist

To confirm the repository is healthy in a clean environment:

```bash
uv lock --check
uv sync
uv run manage.py check
uv run manage.py findstatic css/base.css
uv run manage.py collectstatic --noinput
uv run ruff check --no-fix
```
