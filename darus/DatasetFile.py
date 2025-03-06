from typing import Tuple
import warnings
import zipfile
import validators
import hashlib
import humanize
from tqdm.auto import tqdm
from typing import Tuple
import requests
import os
from pathlib import Path
from urllib.parse import urlparse


class DatasetFile:
    def __init__(self, json: dict, server_url: str):
        """
        Creates an instance of a dataset file.

        :param json: the json information containing the required information for the dataset file
        :type json: dict
        :param server_url: The url of the server where the dataset is stored
        :type server_url: str

        :raise KeyError: If a required key is not in json. See get_required_keys for a list of the keys.
        :raise ValueError: If the server_url concatenated with the other information is not a valid url.
        """
        self.__description = json["description"] if "description" in json else ""
        self.__sub_dir = json["directoryLabel"] if "directoryLabel" in json else ""
        data_file = json["dataFile"]
        self.__id = data_file["id"]
        self.__persistentId = data_file["persistentId"]
        self.__filesize = data_file["filesize"]
        self.name = data_file["filename"]
        self.__hash = data_file["checksum"]["value"]
        self.parsed_server_url = urlparse(server_url)

        self._url = self.parsed_server_url._replace(
            path=f"api/access/datafile/{self.__id}/", query=str("format=original")
        ).geturl()

        # Check for original file
        if "originalFileName" in data_file:
            self._url = urlparse(self._url)._replace(query="format=original").geturl()
            self.name = data_file["originalFileName"]

        self.__file_path = None  # Will be set if downloaded successfully

        if not validators.url(self._url):
            raise ValueError(f"The url {self._url} is not valid.")

    def __str__(self) -> str:
        """Overrides implementation of string"""
        return f"{self.name} [{self.get_filesize()}]: {self.__description}"

    def get_required_keys(self) -> Tuple[str]:
        """Returns the required keys in the json object passed to the constructor"""
        return ("id", "persistentId", "filesize", "filename")

    def get_hash(self) -> str:
        """Returns the md5 hash value of the file"""
        return self.__hash

    def get_filesize(self, pretty: bool = True) -> str:
        """
        Returns the size of the file

        :param pretty: If True, returns the filesize in a human readable form (MB, GB, etc.)
        :type pretty: bool
        :return: The filesize of the dataset file
        :rtype: str
        """
        return humanize.naturalsize(self.__filesize) if pretty else self.__filesize

    def download(self, path="", header=None, block_size=1024) -> bool:
        """
        Downloads the file based on self._url and saves it to path/self.filename
        Credits: https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests

        :param path: The path to save the file
        :type path: str
        :param header: The header if needed for the web requests [Default: None]
        :type header: dict
        :param block_size: The size to iterate over the response [Default: 1024]
        :type block_size: int
        :return: True if downloaded file is valid.
        :rtype: bool

        :raise ValueError: If block_size is <= 0
        """
        if block_size <= 0:
            raise ValueError("block_size must be >0.")

        successful = False
        try:
            dir = Path(path) / self.__sub_dir
            dir.mkdir(parents=True, exist_ok=True)

            file_path = dir / self.name

            print(f"Downloading {file_path}...")

            response = requests.get(self._url, headers=header, stream=True)
            response.raise_for_status()

            with tqdm(
                total=self.__filesize, unit="B", unit_scale=True, dynamic_ncols=True
            ) as progress_bar:
                with open(file_path, "wb") as file:
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        file.write(data)

            successful = self.validate(file_path)

            if successful:
                self.__file_path = file_path

        except FileExistsError as fe:
            print(
                f"The subdirectory '{dir}' could not be created, but is expected from {self.name}."
            )
        except requests.exceptions.HTTPError as he:
            print(
                f"Error wile trying to download '{self.name}' from '{self._url}'.\n{he}"
            )
        except Exception as e:
            print(f"Uncatched error.\n{e}")

        return successful

    def validate(self, file_path) -> bool:
        """
        Validates a file against an MD5 hash value
        Credits: https://gist.github.com/mjohnsullivan/9322154

        :param file_path: path to the file for hash validation
        :type file_path: string
        :return: True if the hashes are the same, False otherwise.
        :rtype: bool
        """

        hash = self.__hash
        with open(file_path, "rb") as f:
            md5_hash = hashlib.md5(f.read()).hexdigest()
        return md5_hash == hash

    def remove_file(self):
        """
        Removes the downloaded file.
        """

        if self.__file_path and os.path.isfile(self.__file_path):
            try:
                os.remove(self.__file_path)
            except OsError as e:
                print(f"Error while trying to delete {self.__file_path}")
            else:
                return True
        else:
            warnings.warn(
                f"Attempt to delete '{self.name}' failed. File not found in {self.__file_path}."
            )
            return False

    def extract_file(self):
        """Extracts the file, if it ends with .zip"""
        if (
            self.__file_path
            and os.path.isfile(self.__file_path)
            and self.__file_path.suffix == ".zip"
        ):
            try:
                with zipfile.ZipFile(self.__file_path, "r") as zip_ref:
                    zip_ref.extractall(self.__file_path.parent)
            except Exception as e:
                print(f"Error while trying to extrac {self.name}.\n{e}")
                return False
            else:
                return True
        else:
            return False
