import pytest
import tempfile
from pathlib import Path
from tests.fixtures.test_data import (
    DEMO_SERVER_URL,
    DEMO_DATASET_URLS,
    MOCK_FILE_INFO,
    TEST_CONFIG,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test downloads."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def demo_server_url():
    """Demo Dataverse server URL for testing."""
    return DEMO_SERVER_URL


@pytest.fixture
def demo_dataset_urls():
    """Demo dataset URLs for integration testing."""
    return DEMO_DATASET_URLS


@pytest.fixture
def mock_file_info():
    """Mock file information for DatasetFile unit tests."""
    return MOCK_FILE_INFO


@pytest.fixture
def invalid_url():
    """Invalid URL for negative testing."""
    return "not-a-valid-url"


@pytest.fixture
def test_config():
    """Test configuration settings."""
    return TEST_CONFIG
