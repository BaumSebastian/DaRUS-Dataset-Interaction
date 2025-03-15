import zipfile
import validators
import hashlib
import humanize
import requests
import os
from pathlib import Path
from urllib.parse import urlparse


class DatasetFile:
    def __init__(self, json: dict, server_url: str, download_original: bool = True):
        """
        Creates an instance of a dataset file.

        :param json: the json information containing the required information for the dataset file
        :type json: dict
        :param server_url: The url of the server where the dataset is stored
        :type server_url: str
        :param download_original: Indicates that if a original file exists, if it should be downloaded instead [Default: bool]
        :type download_original: bool

        :raise KeyError: If a required key is not in json. See get_required_keys for a list of the keys.
        :raise ValueError: If the server_url concatenated with the other information is not a valid url.
        """
        self.description = json["description"] if "description" in json else ""
        self.sub_dir = json["directoryLabel"] if "directoryLabel" in json else ""
        data_file = json["dataFile"]
        self.__id = data_file["id"]
        self.__persistentId = data_file["persistentId"]
        self.__filesize = data_file["filesize"]
        self.name = data_file["filename"]
        self.__hash = data_file["checksum"]["value"]
        self.has_original = "originalFileName" in data_file
        self.download_original = download_original
        self.original_file_name = (
            data_file["originalFileName"] if self.has_original else ""
        )
        self.friendly_type = (
            data_file["friendlyType"] if "friendlyType" in data_file else ""
        )
        self.do_extract = self.friendly_type == "ZIP Archive"
        self.file_path = None  # Will be set if downloaded successfully

        self.parsed_server_url = urlparse(server_url)
        self._url = self.parsed_server_url._replace(
            path=f"api/access/datafile/{self.__id}/"
        ).geturl()

        if not validators.url(self._url):
            raise ValueError(f"The url {self._url} is not valid.")

    def __str__(self) -> str:
        """Overrides implementation of string"""
        return f"{self.name} [{self.get_filesize()}] - {self.description}"

    def get_filesize(self, pretty: bool = True) -> str:
        """
        Returns the size of the file

        :param pretty: If True, returns the filesize in a human readable form (MB, GB, etc.)
        :type pretty: bool
        :return: The filesize of the dataset file
        :rtype: str
        """
        return humanize.naturalsize(self.__filesize) if pretty else self.__filesize

    def download(self, path="", header=None, chunk_size=8192) -> int:
        """
        Downloads the file based on self._url and saves it to path/self.filename
        Credits: https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests

        :param path: The path to save the file
        :type path: str
        :param header: The header if needed for the web requests [Default: None]
        :type header: dict
        :param chunk_size: The size to iterate over the response [Default: 1024]
        :type chunk_size: int
        :yields: The downloaded bytes so far.
        """
        # Check for original file
        name = self.name
        url = self._url

        if self.download_original:
            url = urlparse(self._url)._replace(query="format=original").geturl()
            name = self.original_file_name if self.original_file_name else self.name

        try:
            dir = Path(path) / self.sub_dir
            dir.mkdir(parents=True, exist_ok=True)

            file_path = dir / name
            self.file_path = file_path

            downloaded = 0
            with requests.get(url, headers=header, stream=True) as r:
                r.raise_for_status()
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        downloaded += len(chunk)
                        yield (downloaded)
                        f.write(chunk)
        except FileExistsError as fe:
            print(
                f"The subdirectory '{dir}' could not be created, but is expected from {self.name}."
            )
        except requests.exceptions.HTTPError as he:
            print(
                f"Error wile trying to download '{self.name}' from '{self._url}'.\n{he}"
            )
        except MemoryError as me:
            print(f"MemoryError encountered while downloading '{self.name}'.\n{me}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def validate(self, chunk_size=8192) -> bool:
        """
        Validates a file against an MD5 hash value
        Credits: https://gist.github.com/mjohnsullivan/9322154

        :param file_path: path to the file for hash validation
        :type file_path: string
        :return: True if the hashes are the same, False otherwise or the file not exists.
        :rtype: bool
        """

        if not self.file_path or not self.__hash:
            return False

        m = hashlib.md5()
        with open(self.file_path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                m.update(chunk)

        return m.hexdigest() == self.__hash

    def remove(self):
        """
        Removes the downloaded file.
        """
        removed_successfully = False
        if self.file_path and os.path.isfile(self.file_path):
            try:
                os.remove(self.file_path)
            except OsError as e:
                print(f"Error while trying to delete {self.file_path}")
            else:
                removed_successfully = True
        return removed_successfully

    def process(self):
        """post process the file."""
        processed_successfully = True

        if self.file_path and os.path.isfile(self.file_path):
            # process zip files
            if self.file_path.suffix == ".zip":
                try:
                    with zipfile.ZipFile(self.file_path, "r") as zip_ref:
                        zip_ref.extractall(self.file_path.parent)
                except Exception as e:
                    print(f"Error while trying to extract {self.file_path}.\n{e}")
                    processed_successfully = False
        return processed_successfully
