"""Unit tests for the DatasetFile class."""

import json
import pytest
import responses
import hashlib
import zipfile
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from darus.DatasetFile import DatasetFile


class TestDatasetFileInitialization:
    """Test DatasetFile class initialization and validation."""

    def test_basic_file_initialization(self, mock_file_info):
        """Test DatasetFile initialization with basic file info."""
        server_url = "https://demo.dataverse.org"

        file = DatasetFile(mock_file_info, server_url)

        assert file.name == "test_file.txt"
        assert file.description == "Test file description"
        assert file.sub_dir == "test_dir"
        assert file.get_filesize(pretty=False) == 1024
        assert file.friendly_type == "Plain Text"
        assert file.has_original is False
        assert file.do_extract is False

    def test_file_with_original_filename(self):
        """Test DatasetFile with original filename."""
        file_info = {
            "description": "Test CSV file",
            "directoryLabel": "",
            "dataFile": {
                "id": 98766,
                "persistentId": "doi:10.70122/FK2/test-csv",
                "filename": "data.tab",
                "originalFileName": "data.csv",
                "filesize": 2048,
                "checksum": {"value": "abc123"},
                "friendlyType": "Comma Separated Values",
            },
        }
        server_url = "https://demo.dataverse.org"

        file = DatasetFile(file_info, server_url)

        assert file.name == "data.tab"
        assert file.original_file_name == "data.csv"
        assert file.has_original is True

    def test_zip_file_extraction_flag(self):
        """Test that ZIP files are marked for extraction."""
        file_info = {
            "description": "ZIP archive",
            "directoryLabel": "archives",
            "dataFile": {
                "id": 98767,
                "persistentId": "doi:10.70122/FK2/test-zip",
                "filename": "archive.zip",
                "filesize": 1048576,
                "checksum": {"value": "def456"},
                "friendlyType": "ZIP Archive",
            },
        }
        server_url = "https://demo.dataverse.org"

        file = DatasetFile(file_info, server_url)

        assert file.do_extract is True
        assert file.friendly_type == "ZIP Archive"

    def test_invalid_server_url_raises_error(self, mock_file_info):
        """Test that invalid server URL raises ValueError."""
        invalid_server = "not-a-valid-url"

        with pytest.raises(ValueError, match="The url .* is not valid"):
            DatasetFile(mock_file_info, invalid_server)

    def test_missing_optional_fields(self):
        """Test DatasetFile with missing optional fields."""
        minimal_file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/minimal",
                "filename": "minimal.txt",
                "filesize": 512,
                "checksum": {"value": "minimal123"},
            }
        }
        server_url = "https://demo.dataverse.org"

        file = DatasetFile(minimal_file_info, server_url)

        assert file.description == ""
        assert file.sub_dir == ""
        assert file.friendly_type == ""


class TestDatasetFileString:
    """Test DatasetFile string representation."""

    def test_string_representation(self, mock_file_info):
        """Test __str__ method output."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        str_repr = str(file)

        assert "test_file.txt" in str_repr
        assert "1.0 kB" in str_repr  # humanized file size
        assert "Test file description" in str_repr


class TestDatasetFileSize:
    """Test file size formatting."""

    def test_pretty_file_size(self, mock_file_info):
        """Test humanized file size formatting."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        pretty_size = file.get_filesize(pretty=True)
        raw_size = file.get_filesize(pretty=False)

        assert pretty_size == "1.0 kB"
        assert raw_size == 1024

    def test_large_file_size(self):
        """Test file size formatting for large files."""
        large_file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/large",
                "filename": "large.dat",
                "filesize": 1073741824,  # 1 GB
                "checksum": {"value": "large123"},
            }
        }
        server_url = "https://demo.dataverse.org"

        file = DatasetFile(large_file_info, server_url)

        assert "GB" in file.get_filesize(pretty=True)
        assert file.get_filesize(pretty=False) == 1073741824


class TestDatasetFileDownload:
    """Test DatasetFile download functionality."""

    def test_successful_download(self, mock_file_info, temp_dir):
        """Test successful file download."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        test_content = b"Test file content"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{server_url}/api/access/datafile/98765/",
                body=test_content,
                status=200,
            )

            # Consume the download generator
            download_progress = list(file.download(temp_dir))

            assert len(download_progress) > 0
            assert file.file_path is not None
            assert file.file_path.exists()

            # Verify file content
            with open(file.file_path, "rb") as f:
                assert f.read() == test_content

    def test_download_original_format(self, temp_dir):
        """Test downloading original file format."""
        file_info = {
            "description": "CSV file",
            "directoryLabel": "",
            "dataFile": {
                "id": 98766,
                "persistentId": "doi:10.70122/FK2/csv-test",
                "filename": "data.tab",
                "originalFileName": "data.csv",
                "filesize": 100,
                "checksum": {"value": "csv123"},
                "friendlyType": "Comma Separated Values",
            },
        }
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(file_info, server_url, download_original=True)

        test_content = b"col1,col2\nval1,val2"

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{server_url}/api/access/datafile/98766/?format=original",
                body=test_content,
                status=200,
            )

            list(file.download(temp_dir))

            # Should download with original filename
            assert file.file_path.name == "data.csv"

    def test_download_with_subdirectory(self, mock_file_info, temp_dir):
        """Test download creates subdirectories."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                f"{server_url}/api/access/datafile/98765/",
                body=b"content",
                status=200,
            )

            list(file.download(temp_dir))

            # Should create subdirectory
            expected_path = temp_dir / "test_dir" / "test_file.txt"
            assert file.file_path == expected_path
            assert expected_path.parent.exists()

    def test_download_http_error(self, mock_file_info, temp_dir):
        """Test download handles HTTP errors gracefully."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET, f"{server_url}/api/access/datafile/98765/", status=404
            )

            with patch("builtins.print") as mock_print:
                list(file.download(temp_dir))

                mock_print.assert_called()
                assert "Error wile trying to download" in str(mock_print.call_args)

    def test_download_memory_error(self, mock_file_info, temp_dir):
        """Test download handles memory errors."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.iter_content.side_effect = MemoryError("Out of memory")
            mock_get.return_value.__enter__.return_value = mock_response

            with patch("builtins.print") as mock_print:
                list(file.download(temp_dir))

                mock_print.assert_called()
                assert "MemoryError" in str(mock_print.call_args)


class TestDatasetFileValidation:
    """Test DatasetFile hash validation."""

    def test_successful_validation(self, temp_dir):
        """Test successful MD5 hash validation."""
        # Create a test file with known content and hash
        test_content = b"Hello, World!"
        expected_hash = hashlib.md5(test_content).hexdigest()

        file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/validation-test",
                "filename": "test.txt",
                "filesize": len(test_content),
                "checksum": {"value": expected_hash},
            }
        }

        server_url = "https://demo.dataverse.org"
        file = DatasetFile(file_info, server_url)

        # Create the test file
        test_file = temp_dir / "test.txt"
        test_file.write_bytes(test_content)
        file.file_path = test_file

        assert file.validate() is True

    def test_failed_validation_wrong_hash(self, temp_dir):
        """Test validation failure with wrong hash."""
        test_content = b"Hello, World!"
        wrong_hash = "wrong_hash_value"

        file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/wrong-hash",
                "filename": "test.txt",
                "filesize": len(test_content),
                "checksum": {"value": wrong_hash},
            }
        }

        server_url = "https://demo.dataverse.org"
        file = DatasetFile(file_info, server_url)

        # Create the test file
        test_file = temp_dir / "test.txt"
        test_file.write_bytes(test_content)
        file.file_path = test_file

        assert file.validate() is False

    def test_validation_no_file_path(self, mock_file_info):
        """Test validation returns False when no file path is set."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        # file.file_path is None by default
        assert file.validate() is False

    def test_validation_no_hash(self, temp_dir):
        """Test validation returns False when no hash is provided."""
        file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/no-hash",
                "filename": "test.txt",
                "filesize": 100,
                "checksum": {"value": None},
            }
        }

        server_url = "https://demo.dataverse.org"
        file = DatasetFile(file_info, server_url)

        test_file = temp_dir / "test.txt"
        test_file.write_text("content")
        file.file_path = test_file

        assert file.validate() is False


class TestDatasetFileRemoval:
    """Test DatasetFile removal functionality."""

    def test_successful_file_removal(self, temp_dir):
        """Test successful file removal."""
        file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/remove-test",
                "filename": "to_remove.txt",
                "filesize": 100,
                "checksum": {"value": "abc123"},
            }
        }

        server_url = "https://demo.dataverse.org"
        file = DatasetFile(file_info, server_url)

        # Create the test file
        test_file = temp_dir / "to_remove.txt"
        test_file.write_text("content to remove")
        file.file_path = test_file

        assert test_file.exists()
        result = file.remove()

        assert result is True
        assert not test_file.exists()

    def test_remove_nonexistent_file(self, mock_file_info):
        """Test removing a file that doesn't exist."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        file.file_path = Path("/nonexistent/path/file.txt")

        result = file.remove()
        assert result is False

    def test_remove_no_file_path(self, mock_file_info):
        """Test remove when no file path is set."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        # file.file_path is None by default
        result = file.remove()
        assert result is False


class TestDatasetFileProcessing:
    """Test DatasetFile post-processing functionality."""

    def test_zip_extraction_success(self, temp_dir):
        """Test successful ZIP file extraction."""
        file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/zip-test",
                "filename": "test.zip",
                "filesize": 1000,
                "checksum": {"value": "zip123"},
                "friendlyType": "ZIP Archive",
            }
        }

        server_url = "https://demo.dataverse.org"
        file = DatasetFile(file_info, server_url)

        # Create a real ZIP file for testing
        zip_path = temp_dir / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("file1.txt", "Content of file 1")
            zf.writestr("file2.txt", "Content of file 2")

        file.file_path = zip_path

        result = file.process()

        assert result is True
        assert (temp_dir / "file1.txt").exists()
        assert (temp_dir / "file2.txt").exists()

    def test_zip_extraction_error(self, temp_dir):
        """Test ZIP extraction with corrupted file."""
        file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/corrupted-zip",
                "filename": "corrupted.zip",
                "filesize": 100,
                "checksum": {"value": "corrupt123"},
                "friendlyType": "ZIP Archive",
            }
        }

        server_url = "https://demo.dataverse.org"
        file = DatasetFile(file_info, server_url)

        # Create a corrupted ZIP file
        corrupted_zip = temp_dir / "corrupted.zip"
        corrupted_zip.write_bytes(b"This is not a valid ZIP file")
        file.file_path = corrupted_zip

        with patch("builtins.print") as mock_print:
            result = file.process()

            assert result is False
            mock_print.assert_called()

    def test_non_zip_processing(self, temp_dir):
        """Test processing of non-ZIP files (should do nothing)."""
        file_info = {
            "dataFile": {
                "id": 12345,
                "persistentId": "doi:10.70122/FK2/txt-test",
                "filename": "regular.txt",
                "filesize": 100,
                "checksum": {"value": "txt123"},
                "friendlyType": "Plain Text",
            }
        }

        server_url = "https://demo.dataverse.org"
        file = DatasetFile(file_info, server_url)

        # Create a regular text file
        text_file = temp_dir / "regular.txt"
        text_file.write_text("Regular text content")
        file.file_path = text_file

        result = file.process()

        # Should succeed but do nothing for non-ZIP files
        assert result is True

    def test_process_no_file_path(self, mock_file_info):
        """Test process when no file path is set."""
        server_url = "https://demo.dataverse.org"
        file = DatasetFile(mock_file_info, server_url)

        # file.file_path is None by default
        result = file.process()
        assert result is True  # Should succeed but do nothing
