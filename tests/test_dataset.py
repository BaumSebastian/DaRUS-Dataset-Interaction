"""Unit tests for the Dataset class."""

import json
import pytest
import responses
from unittest.mock import patch, MagicMock
from pathlib import Path

from darus import Dataset
from darus.DatasetFile import DatasetFile


class TestDatasetInitialization:
    """Test Dataset class initialization and validation."""

    def test_valid_url_initialization(self, demo_dataset_urls):
        """Test Dataset initialization with valid URL."""
        url = demo_dataset_urls[0]

        # Mock the HTTP request to avoid network calls
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url)

            assert dataset.url.geturl() == url
            assert dataset.server_url == "https://demo.dataverse.org"
            assert dataset.persistent_id == "doi:10.70122/FK2/TEST"
            assert dataset.title == "Test Dataset"
            assert len(dataset.authors) == 2
            assert "Test Author 1" in dataset.authors

    def test_invalid_url_raises_error(self, invalid_url):
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError, match="Provided url is not valid"):
            Dataset(invalid_url)

    def test_api_token_header_setup(self, demo_dataset_urls):
        """Test API token is properly set in headers."""
        url = demo_dataset_urls[0]
        api_token = "test-token-123"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url, api_token=api_token)

            assert dataset.header == {"X-Dataverse-key": api_token}

    def test_no_api_token_header_none(self, demo_dataset_urls):
        """Test header is None when no API token provided."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url)

            assert dataset.header is None


class TestDatasetInformationRetrieval:
    """Test dataset information retrieval from API."""

    def test_successful_api_response(self, demo_dataset_urls):
        """Test successful parsing of API response."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url)

            assert dataset.persistent_id == "doi:10.70122/FK2/TEST"
            assert dataset.title == "Test Dataset"
            assert dataset.license_name == "CC BY 4.0"
            assert dataset.version_state == "RELEASED"
            assert len(dataset.download_files) == 2
            assert isinstance(dataset.download_files[0], DatasetFile)

    def test_http_error_handling(self, demo_dataset_urls):
        """Test handling of HTTP errors."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                status=404,
            )

            with patch("builtins.print") as mock_print:
                dataset = Dataset(url)

                assert len(dataset.download_files) == 0
                mock_print.assert_called()

    def test_invalid_json_response(self, demo_dataset_urls):
        """Test handling of invalid JSON response."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                body="invalid json",
                status=200,
            )

            with patch("builtins.print") as mock_print:
                dataset = Dataset(url)

                assert len(dataset.download_files) == 0
                mock_print.assert_called()

    def test_missing_keys_in_response(self, demo_dataset_urls):
        """Test handling of missing keys in API response."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json={"data": {"incomplete": "data"}},
                status=200,
            )

            with patch("builtins.print") as mock_print:
                dataset = Dataset(url)

                assert len(dataset.download_files) == 0
                mock_print.assert_called()


class TestDatasetSummary:
    """Test Dataset summary functionality."""

    def test_summary_output(self, demo_dataset_urls):
        """Test summary method prints dataset information."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url)

            with patch("rich.console.Console.print") as mock_print:
                dataset.summary()

                # Should print two tables: Dataset Summary and Files in Dataset
                assert mock_print.call_count == 2

    def test_format_datetime(self, demo_dataset_urls):
        """Test datetime formatting utility."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url)

            formatted = dataset.format_datetime("2025-03-12T12:32:17Z")
            assert "2025-03-12 12:32:17" in formatted

            # Test None handling
            assert dataset.format_datetime(None) == ""


class TestDatasetDownload:
    """Test Dataset download functionality."""

    def test_download_with_valid_path(self, demo_dataset_urls, temp_dir):
        """Test download method with valid path."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url)

            # Mock all file downloads before calling dataset.download
            with patch.object(dataset.download_files[0], "download") as mock_download1, \
                 patch.object(dataset.download_files[0], "validate") as mock_validate1, \
                 patch.object(dataset.download_files[1], "download") as mock_download2, \
                 patch.object(dataset.download_files[1], "validate") as mock_validate2:
                
                mock_download1.return_value = iter([1024])
                mock_validate1.return_value = True
                mock_download2.return_value = iter([2048])
                mock_validate2.return_value = True

                dataset.download(str(temp_dir))

                mock_download1.assert_called_once()
                mock_validate1.assert_called_once()
                mock_download2.assert_called_once()
                mock_validate2.assert_called_once()

    def test_download_specific_files(self, demo_dataset_urls, temp_dir):
        """Test downloading specific files only."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url)

            # Mock file downloads
            with patch.object(
                dataset.download_files[0], "download"
            ) as mock_download, patch.object(
                dataset.download_files[0], "validate"
            ) as mock_validate:
                mock_download.return_value = iter([1024])
                mock_validate.return_value = True

                # Download only the first file (use actual filename from mock)
                dataset.download(str(temp_dir), files=["metadata.tab"])

                # Only the first file should be downloaded
                mock_download.assert_called_once()

    def test_download_post_processing(self, demo_dataset_urls, temp_dir):
        """Test download with post processing enabled."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json=TestDatasetDownload._mock_dataset_response(),
                status=200,
            )

            dataset = Dataset(url)

            # Mock both files - focus on ZIP file that needs processing
            first_file = dataset.download_files[0]  # First file
            zip_file = dataset.download_files[1]  # Second file is ZIP

            with patch.object(first_file, "download") as mock_download1, \
                 patch.object(first_file, "validate") as mock_validate1, \
                 patch.object(zip_file, "download") as mock_download2, \
                 patch.object(zip_file, "validate") as mock_validate2, \
                 patch.object(zip_file, "process") as mock_process, \
                 patch.object(zip_file, "remove") as mock_remove, \
                 patch("rich.console.Console.print") as mock_console_print:

                # Mock first file (no processing)
                mock_download1.return_value = iter([1024])
                mock_validate1.return_value = True
                
                # Mock ZIP file (with processing)
                mock_download2.return_value = iter([2048])
                mock_validate2.return_value = True
                mock_process.return_value = True
                mock_remove.return_value = True
                zip_file.do_extract = True

                dataset.download(str(temp_dir), post_process=True, remove_after_pp=True)

                # Verify ZIP processing was called
                mock_process.assert_called_once()
                mock_remove.assert_called_once()

    def test_no_files_to_download(self, demo_dataset_urls, temp_dir):
        """Test download when no files are available."""
        url = demo_dataset_urls[0]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                "https://demo.dataverse.org/api/datasets/:persistentId/",
                json={
                    "status": "OK",
                    "data": {
                        "latestVersion": {
                            "datasetPersistentId": "doi:10.70122/FK2/TEST",
                            "files": [],
                        }
                    },
                },
                status=200,
            )

            dataset = Dataset(url)

            with patch("builtins.print") as mock_print:
                dataset.download(str(temp_dir))

                mock_print.assert_called_with("No files to download.")

    @staticmethod
    def _mock_dataset_response():
        """Helper method to create mock dataset API response."""
        return {
            "status": "OK",
            "data": {
                "latestVersion": {
                    "datasetPersistentId": "doi:10.70122/FK2/TEST",
                    "versionState": "RELEASED",
                    "lastUpdateTime": "2025-03-12T12:32:17Z",
                    "createTime": "2025-01-15T10:00:00Z",
                    "license": {"name": "CC BY 4.0"},
                    "metadataBlocks": {
                        "citation": {
                            "fields": [
                                {"typeName": "title", "value": "Test Dataset"},
                                {
                                    "typeName": "author",
                                    "value": [
                                        {"authorName": {"value": "Test Author 1"}},
                                        {"authorName": {"value": "Test Author 2"}},
                                    ],
                                },
                            ]
                        }
                    },
                    "files": [
                        {
                            "description": "Test metadata file",
                            "directoryLabel": "",
                            "dataFile": {
                                "id": 12345,
                                "persistentId": "doi:10.70122/FK2/TEST/file1",
                                "filename": "metadata.tab",
                                "originalFileName": "metadata.csv",
                                "filesize": 2621440,
                                "checksum": {
                                    "value": "d41d8cd98f00b204e9800998ecf8427e"
                                },
                                "friendlyType": "Comma Separated Values",
                            },
                        },
                        {
                            "description": "Test ZIP archive",
                            "directoryLabel": "data",
                            "dataFile": {
                                "id": 12346,
                                "persistentId": "doi:10.70122/FK2/TEST/file2",
                                "filename": "test_data.zip",
                                "filesize": 104857600,
                                "checksum": {
                                    "value": "5d41402abc4b2a76b9719d911017c592"
                                },
                                "friendlyType": "ZIP Archive",
                            },
                        },
                    ],
                }
            },
        }


# Add the same helper method to other test classes
TestDatasetInitialization._mock_dataset_response = (
    TestDatasetDownload._mock_dataset_response
)
TestDatasetInformationRetrieval._mock_dataset_response = (
    TestDatasetDownload._mock_dataset_response
)
TestDatasetSummary._mock_dataset_response = TestDatasetDownload._mock_dataset_response
