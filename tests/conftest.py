"""
Pytest configuration and fixtures for CTFd test suite performance optimization.

This module provides session-scoped fixtures and database transaction rollback
patterns to eliminate the overhead of creating/destroying databases for each test.
"""

import pytest
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker

from CTFd import create_app
from CTFd.models import db
from tests.helpers import setup_ctfd, destroy_ctfd
from CTFd.config import TestingConfig


@pytest.fixture(scope="session")
def base_app():
    """Create a base CTFd application instance for the entire test session."""
    # Create app without setup to avoid duplicate initialization
    app = create_app(TestingConfig)
    return app


@pytest.fixture(scope="session") 
def configured_app(base_app):
    """Setup the CTFd application with initial configuration."""
    app = setup_ctfd(
        base_app,
        ctf_name="CTFd",
        ctf_description="CTF description", 
        name="admin",
        email="admin@examplectf.com",
        password="password",
        user_mode="users"
    )
    
    yield app
    
    # Cleanup at end of session
    destroy_ctfd(app)


@pytest.fixture
def app(configured_app):
    """
    Provide application with database transaction rollback for test isolation.
    
    This fixture creates a database transaction at the start of each test
    and rolls it back at the end, providing test isolation without the
    overhead of database recreation.
    """
    with configured_app.app_context():
        # Start a transaction
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use the transaction
        db.session.configure(bind=connection)
        
        yield configured_app
        
        # Rollback transaction and close connection
        db.session.remove()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(app):
    """Provide a test client with transaction rollback."""
    return app.test_client()


@pytest.fixture
def admin_client(app):
    """Provide a pre-authenticated admin test client."""
    from tests.helpers import login_as_user
    return login_as_user(app, name="admin", password="password")


@pytest.fixture
def user_factory(app):
    """Factory for creating test users within transaction scope."""
    from tests.helpers import gen_user
    import uuid
    
    def _create_user(**kwargs):
        # Generate unique values to avoid constraint violations
        unique_suffix = str(uuid.uuid4())[:8]
        defaults = {
            "name": f"test_user_{unique_suffix}",
            "email": f"test_{unique_suffix}@example.com", 
            "password": "password"
        }
        defaults.update(kwargs)
        return gen_user(app.db, **defaults)
    
    return _create_user


@pytest.fixture
def challenge_factory(app):
    """Factory for creating test challenges within transaction scope."""
    from tests.helpers import gen_challenge
    import uuid
    
    def _create_challenge(**kwargs):
        # Generate unique values to avoid constraint violations
        unique_suffix = str(uuid.uuid4())[:8]
        defaults = {
            "name": f"test_challenge_{unique_suffix}",
            "description": "Test challenge description",
            "value": 100,
            "category": "test",
            "type": "standard",
            "state": "visible"
        }
        defaults.update(kwargs)
        return gen_challenge(app.db, **defaults)
    
    return _create_challenge


@pytest.fixture
def team_factory(app):
    """Factory for creating test teams within transaction scope."""
    from tests.helpers import gen_team
    
    def _create_team(**kwargs):
        defaults = {
            "name": "test_team",
            "email": "team@example.com",
            "password": "password",
            "member_count": 4
        }
        defaults.update(kwargs)
        return gen_team(app.db, **defaults)
    
    return _create_team


@pytest.fixture
def flag_factory(app):
    """Factory for creating test flags within transaction scope."""
    from tests.helpers import gen_flag
    
    def _create_flag(challenge_id, **kwargs):
        defaults = {
            "content": "flag{test}",
            "type": "static"
        }
        defaults.update(kwargs)
        return gen_flag(app.db, challenge_id=challenge_id, **defaults)
    
    return _create_flag


# Performance optimization: Disable SQLAlchemy echo for tests
@pytest.fixture(autouse=True)
def disable_db_echo(app):
    """Disable SQLAlchemy echo for better test performance."""
    with app.app_context():
        db.engine.echo = False


# Performance optimization: Configure faster test database settings
@pytest.fixture(scope="session", autouse=True)
def configure_test_db_performance():
    """Configure database settings for optimal test performance."""
    # These settings can be overridden by individual tests if needed
    import os
    os.environ.setdefault('SQLALCHEMY_ENGINE_OPTIONS_POOL_RECYCLE', '-1')
    os.environ.setdefault('SQLALCHEMY_ENGINE_OPTIONS_POOL_PRE_PING', 'false')