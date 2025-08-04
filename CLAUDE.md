# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## CTFd - Capture The Flag Framework

CTFd is a CTF (Capture The Flag) framework built in Python/Flask focusing on ease of use and customizability. It provides everything needed to run a CTF competition with support for plugins and themes.

## Key Development Commands

### Running the Application
- `python serve.py` - Start development server on port 4000 (default)
- `python serve.py --port 8080` - Start on custom port
- `flask run` - Alternative way to start the application
- `make serve` - Start using Makefile

### Testing
- `make test` - Run full test suite with coverage, bandit security checks, and dependency analysis
- `pytest` - Run tests directly
- Individual tests can be run with `pytest tests/path/to/test_file.py`

### Code Quality
- `make lint` - Run all linting tools (ruff, isort, black, prettier)
- `make format` - Auto-format code using isort, black, and prettier
- `ruff check --select E,F,W,B,C4,I --ignore E402,E501,E712,B904,B905,I001 --exclude=CTFd/uploads CTFd/` - Python linting
- `black --check --diff --exclude=CTFd/uploads --exclude=node_modules .` - Python code formatting check

### Database Management
- `python manage.py shell` - Open application shell for database operations
- Uses Flask-Migrate for database migrations (located in `migrations/`)

### Frontend Development
- Admin theme uses Yarn: `yarn --cwd CTFd/themes/admin lint`
- Themes are located in `CTFd/themes/`
- Static assets are compiled and bundled

## Architecture Overview

### Core Application Structure
- **CTFd/__init__.py** - Main application factory (`create_app()`)
- **CTFd/config.py** - Configuration management with environment variable interpolation
- **serve.py** - Development server entry point with gevent monkey patching
- **CTFd/models/** - SQLAlchemy database models
- **CTFd/api/v1/** - REST API endpoints
- **CTFd/admin/** - Admin interface views
- **CTFd/plugins/** - Plugin system architecture
- **CTFd/themes/** - Theme system with multiple themes (admin, core, core-beta)

### Key Components
- **Challenge System**: Pluggable challenge types in `CTFd/plugins/challenges/`
- **User Management**: Individual and team-based competitions
- **Scoring**: Dynamic scoring with automatic tie resolution
- **File Uploads**: Support for local storage and S3-compatible backends
- **Internationalization**: Babel-based translations in `CTFd/translations/`

### Database
- Uses SQLAlchemy ORM with Flask-SQLAlchemy
- Supports MySQL/MariaDB and SQLite
- Migrations handled by Flask-Migrate (Alembic)
- Database models follow standard Flask patterns

### Frontend Architecture
- **Admin Theme**: Modern Vue.js-based admin interface with Vite build system
- **Core Themes**: Traditional server-rendered templates with Jinja2
- Uses Yarn for dependency management in theme directories
- SCSS/CSS compilation with asset bundling

### Plugin System
- Plugins extend functionality through hooks and events
- Located in `CTFd/plugins/`
- Support for custom challenge types, flags, and themes
- Plugin API provides access to models, views, and configuration

### Security Features
- CSRF protection
- Rate limiting and bruteforce protection
- Input sanitization with nh3
- Secure session management
- Email verification and password reset flows

### Configuration
- Uses INI-style configuration files (`CTFd/config.ini`)
- Environment variable interpolation for deployment flexibility
- Supports various email providers (SMTP, Mailgun)
- OAuth integration with MajorLeagueCyber

## Development Notes

- Application uses gevent for improved concurrency (can be disabled with `--disable-gevent`)
- Debug mode includes optional profiling with `--profile` flag
- Custom Flask request class handles subdirectory deployments
- Extensive test coverage with pytest and security scanning with bandit
- Code formatting enforced with black, isort, and prettier
- Multi-language support with Babel translations