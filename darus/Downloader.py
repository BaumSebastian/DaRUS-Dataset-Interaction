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

class Downloader():
    def __init__(self, url:str, header:dict={}, specific_files:list=[]):
        """
        Creates Instance of the Dataloader

        :param url: The url to download the dataset from
        :type url: str
        :param header: The header for the request [Default {}]
        :type header: dict
        :param specific_files: A list of files, that only will be downloaded if the list is not empty [Default []]
        :type specific_files: iterable

        :raise ValueError: If the provided url is not a valid url.
        """
 
        if not validators.url(url):
            raise ValueError(f"Provided url is not valid {url}.")

        if not isinstance(specific_files, list):
            raise ValueError(f"The parameter specific_files needs to be of type iterable")

        if header and not isinstance(header, dict):
            raise ValueError(f"The parameter header needs to be of type dict")

        self.specific_files = specific_files
        self.downloading_files=[]
        self.header = header

        self.url = urlparse(url)
        self.server_url =  self.url._replace(path='', params='', query='', fragment='').geturl()
        self.dataset_url = self.url._replace(path='/api/datasets/:persistentId/').geturl()

        # Dataset information
        self.persistent_id=None
        self.version_state=None
        self.last_update_time=None
        self.create_time=None
        self.license_name=None

        self._get_dataset_information()

    def _get_dataset_information(self):
        """ Extracts the dataset information from the url. """

        try:
            r = requests.get(self.dataset_url, headers=self.header)
            r.raise_for_status()

            dataset_info = json.loads(r.text)["data"]["latestVersion"]
            self.persistent_id=dataset_info['datasetPersistentId']
            self.version_state=dataset_info['versionState']
            self.last_update_time=dataset_info['lastUpdateTime']
            self.create_time=dataset_info["createTime"]
            self.license_name=dataset_info["license"]["name"]
            
            print(self.url)

            file_info = dataset_info['files']
            self.download_files = list(
                map(
                    lambda item_info: DatasetFile(
                        item_info, self.server_url
                    ),
                    file_info,
                )
            )
        except KeyError as ke:
            print(f"An error occured while trying to access web response.\n{ke}\nThe Dataloader will abort in order to avoid unwanted behaviour.")
            self.download_files=[]
        except requests.HTTPError as exception: # Captures response.raise_for_status() - 4xx or 5xx status code. If you remove this, then code will use generic handle        
            print(f"An error occured while trying to access dataset.\n{str(exception)}\nThe Dataloader will abort in order to avoid unwanted behaivour.")
            self.download_files=[]
        except Exception as exception: # Generic error handler for raise Exception('Error in response json') and "Max retries exceeded."
            print(exception)
            self.download_files=[]


    def summary(self):
        """ Gives an Overview of the dataset retrieved information
        
        :raise NotImplementedError: Not implemented
        """
        raise NotImplementedError()

    def start_download(self, path:str, post_process=True, remove_after_pp=True):
        """
        Starts the download
        """

        if not post_process and remove_after_pp:
            remove_after_pp = False
            warnings.warn("Disabled removing files after post processing, as no post processing is desired.")

        path = Path(path)
        if dir_exists(path):
            if len(self.download_files) > 0:
                message = "Downloading:"

                # Check if user wants to download only specific files 
                if self.specific_files:
                    self.download_files = [f for f in self.download_files if f.name in self.specific_files]

                    if len(self.download_files) != len(self.specific_files):
                        warnings.warn("Couln't not get all specific files. The specified files are not all in the url")

                    message = (
                        'Downloading custom set of files (see "FILES" config):'
                    )

                print(f'\n{message}\n{len(message)* "-"}')
                print(
                    *map(
                        lambda file: f"-{file.name} [{file.get_filesize()}]",
                        self.download_files,
                    ),'\n',
                    sep="\n",
                )
                for f in self.download_files:
                    successful = f.download(path, header=self.header)
                    if successful:
                        print(
                            f"Download '{f.name}' successful (hash: {f.get_hash()})"
                        )
                        if post_process:
                            print("extracting file")
                            f.extract_file()
                    else:
                        print(f"Downloading {f.name} not successful.")
            else:
                print(f"No files to download.")
        else:
            print("Download aborted.")
#           except requests.exceptions.HTTPError as err:
#               print("Error while trying to download.")
#               print(err)

