"""Test data and configuration for DaRUS downloader tests."""

# Demo Dataverse server for testing
DEMO_SERVER_URL = "https://demo.dataverse.org"

# Sample demo dataset URLs for testing (real datasets from demo.dataverse.org)
DEMO_DATASET_URLS = [
    f"{DEMO_SERVER_URL}/dataset.xhtml?persistentId=doi:10.70122/FK2/NIVKU0",  # "Test data for OSF"
    f"{DEMO_SERVER_URL}/dataset.xhtml?persistentId=doi:10.70122/FK2/MF7UWA",  # "'t Hekje"
    f"{DEMO_SERVER_URL}/dataset.xhtml?persistentId=doi:10.70122/FK2/IM0OJQ",  # "test"
]

# Test configuration
TEST_CONFIG = {
    "server_url": DEMO_SERVER_URL,
    "timeout": 30,  # seconds for API calls
    "max_download_size": 1024 * 1024,  # 1MB limit for test downloads
}

# Mock file info for unit tests (when we need to test without network calls)
MOCK_FILE_INFO = {
    "description": "Test file description",
    "directoryLabel": "test_dir",
    "dataFile": {
        "id": 98765,
        "persistentId": "doi:10.70122/FK2/test-file",
        "filename": "test_file.txt",
        "filesize": 1024,
        "checksum": {"value": "d41d8cd98f00b204e9800998ecf8427e"},
        "friendlyType": "Plain Text",
    },
}
