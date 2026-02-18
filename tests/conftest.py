"""Pytest configuration and fixtures."""
import pytest
from pathlib import Path

from src.application.di.container import Container
from src.infrastructure.config.settings import Settings


@pytest.fixture
def test_settings():
    """Fixture for test settings."""
    return Settings(
        database_path=":memory:",  # Use in-memory database for tests
        data_directory="tests/fixtures/data"
    )


@pytest.fixture
def container(test_settings):
    """Fixture for DI container with test configuration."""
    container = Container()
    container.config.override(test_settings)
    return container


@pytest.fixture
def sample_data_dir(tmp_path):
    """Fixture for sample data directory."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir
