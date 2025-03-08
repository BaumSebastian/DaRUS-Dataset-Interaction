import re
import json
import requests
import validators
import warnings
from pathlib import Path
from urllib.parse import urlparse


# Custom import
from .DatasetFile import DatasetFile
from .utils import dir_exists


class Dataset:
    def __init__(self, url: str, files: list = [], api_token=None):
        """
        Creates Instance of the Dataloader

        :param url: The url to download the dataset from
        :type url: str
        :param files: A list of files, that will be downloaded from dataset. If the list is empty, whole dataset is downloaded. [Default []]
        :type files: list

        :raise ValueError: If the provided url is not a valid url.
        :raise ValueError: If files is not an instance of iterable.
        """

        if not validators.url(url):
            raise ValueError(f"Provided url is not valid {url}.")

        if not isinstance(files, list):
            raise ValueError(f"The parameter files needs to be of type iterable")

        self.files = files
        self.downloading_files = []
        self.header = {"X-Dataverse-key": api_token} if api_token else None

        self.url = urlparse(url)
        self.server_url = self.url._replace(
            path="", params="", query="", fragment=""
        ).geturl()
        self.dataset_url = self.url._replace(
            path="/api/datasets/:persistentId/"
        ).geturl()

        # Dataset information
        self.persistent_id = None
        self.version_state = None
        self.last_update_time = None
        self.create_time = None
        self.license_name = None

        self._get_dataset_information()

    def _get_dataset_information(self):
        """Extracts the dataset information from the url."""

        try:
            r = requests.get(self.dataset_url, headers=self.header)
            r.raise_for_status()

            dataset_info = json.loads(r.text)["data"]["latestVersion"]
            self.persistent_id = dataset_info["datasetPersistentId"]
            self.version_state = dataset_info["versionState"]
            self.last_update_time = dataset_info["lastUpdateTime"]
            self.create_time = dataset_info["createTime"]
            self.license_name = dataset_info["license"]["name"]

            file_info = dataset_info["files"]
            self.download_files = list(
                map(
                    lambda item_info: DatasetFile(item_info, self.server_url),
                    file_info,
                )
            )
        except KeyError as ke:
            print(
                f"Couldn't find following key in web response:{ke}\nThe Dataloader will abort in order to avoid unwanted behaviour."
            )
            self.download_files = []
        except (
            requests.HTTPError
        ) as exception:  # Captures response.raise_for_status() - 4xx or 5xx status code. If you remove this, then code will use generic handle
            print(
                f"An error occured while trying to access dataset.\n{str(exception)}\nThe Dataloader will abort in order to avoid unwanted behaivour."
            )
            self.download_files = []
        except (
            Exception
        ) as exception:  # Generic error handler for raise Exception('Error in response json') and "Max retries exceeded."
            print(exception)
            self.download_files = []

    def summary(self):
        """Gives an Overview of the dataset retrieved information

        :raise NotImplementedError: Not implemented
        """
        raise NotImplementedError()

    def download(self, path: str, post_process=True, remove_after_pp=True):
        """
        Starts the download
        """

        if not post_process and remove_after_pp:
            remove_after_pp = False
            warnings.warn(
                "Disabled removing files after post processing, as no post processing is desired."
            )

        path = Path(path)
        if dir_exists(path):
            if len(self.download_files) > 0:
                message = "Downloading:"

                # Check if user wants to download only specific files
                if self.files:
                    self.download_files = [
                        f for f in self.download_files if f.name in self.files
                    ]

                    if len(self.download_files) != len(self.files):
                        m = "Couln't not find all specific files."
                        print(
                            f"{m}\n{len(m)*'-'}", 
                            *[" - " + str(f) for f in self.files if f not in list(map(lambda x: x.name, self.download_files))],
                            sep='\n'
                        )

                    message = 'Downloading custom set of files:'

                print(f'\n{message}\n{len(message)* "-"}')
                print(
                    *map(
                        lambda file: " - " + str(file),
                        self.download_files,
                    ),"",
                    sep="\n",
                )
                n_files = len(self.download_files)
                for i, f in enumerate(self.download_files):
                    name = f.name
                    if f.has_original and f.download_original:
                        name = f.original_file_name
                    print(f"Downloading [{i+1:0{len(str(n_files))}d}/{n_files}]: '{name}' into '{Path(path) / f.sub_dir}'")
                    successful = f.download(path, header=self.header)
                    if successful:
                        if post_process:
                            extract_succ = f.extract_file()
                            if remove_after_pp and extract_succ:
                                del_succ = f.remove_file()
                    else:
                        print(f"Downloading {f.name} not successful.")
            else:
                print(f"No files to download.")
        else:
            print("Download aborted.")
