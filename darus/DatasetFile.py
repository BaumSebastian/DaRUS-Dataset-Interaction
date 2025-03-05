from typing import Tuple
import validators
import hashlib
import humanize
from tqdm.auto import tqdm
from typing import Tuple
import requests
import os


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
        self.__id = json["id"]
        self.__persistentId = json["persistentId"]
        self.__filesize = json["filesize"]
        self.name = json["filename"]
        self.__hash = json["checksum"]["value"]
        self.server_url = server_url
        self._url = f"{self.server_url}/api/access/datafile/{self.__id}"

        
        print(json)

        if not validators.url(self._url):
            raise ValueError(f"The url {self._url} is not valid.")

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

        file_path = os.path.join(path, self.name)
        print(f"Downloading {file_path}...")

        response = requests.get(self._url, headers=header, stream=True)

        with tqdm(
            total=self.__filesize, unit="B", unit_scale=True, dynamic_ncols=True
        ) as progress_bar:
            with open(file_path, "wb") as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)

        return self.validate(file_path)

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
