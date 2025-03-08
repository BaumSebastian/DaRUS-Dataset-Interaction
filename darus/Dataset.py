import re
import json
import requests
import validators
import warnings
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime

from rich.console import Console
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn, TimeRemainingColumn, DownloadColumn, TransferSpeedColumn, SpinnerColumn
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

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
        """Gives an Overview of the dataset retrieved information"""
        console = Console()

        # Create a table to display the information
        table = Table(title="Dataset Summary", title_justify="left")

        table.add_column("Property")
        table.add_column("Value")

        # Add rows with rich formatting
        table.add_row("URL", str(self.url.geturl()))
        table.add_row("Persistent ID", str(self.persistent_id))
        table.add_row("Last Update", self.format_datetime(self.last_update_time))
        table.add_row("License", self.license_name)

        # Display the table
        console.print(table)

    def format_datetime(self, timestamp):
        """Formats the datetime for display"""
        return str(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ"))

    def download(self, path: str, post_process=True, remove_after_pp=True):
        """
        Starts the download

        :param path: The path where the files are downloaded.
        :type path: str
        :param post_process: Indicates if the files should be post processed [Default: True].
        :type post_process: bool
        :param remove_after_pp: Indicates if the files should be deleted after being post processed [Default: True].
        :type remove_after_pp: bool
        """

        if not post_process and remove_after_pp:
            remove_after_pp = False
            warnings.warn(
                "Disabled removing files after post processing, as no post processing is desired."
            )

        path = Path(path)
        if dir_exists(path):
            if len(self.download_files) > 0:

                # Check if user wants to download only specific files
                if self.files:
                    self.download_files = [
                        f for f in self.download_files if f.name in self.files
                    ]

                console = Console() 
                table = Table(title="Downloading...", title_justify="left")

                table.add_column("Name", justify="left")
                table.add_column("Size", justify="left")
                table.add_column("Directory", justify="left")
                table.add_column("Download Original", justify="left")
                table.add_column("Description", justify="left")

                for file in self.download_files:
                    table.add_row(file.name, file.get_filesize(), str(path / file.sub_dir), f"[green]✓({file.original_file_name})[/green]" if file.original_file_name else "", file.description)

                console.print(table)

                    # Create a single progress display with ETA and file size
                with Progress(
                    TextColumn("[bold]{task.description}"),
                    BarColumn(),
                    "[progress.percentage]{task.percentage:>3.1f}%",
                    "•",
                    DownloadColumn(),
                    "•",
                    TimeElapsedColumn(),
                    "•",
                    TimeRemainingColumn(),
                    "•",
                    TransferSpeedColumn(),
                    console=console
                ) as progress:

                    for i, f in enumerate(self.download_files):
                        if f.has_original and f.download_original:
                            f.name = f.original_file_name
                        name = f.name

                        # Downloading
                        task_id = progress.add_task(f"[blue]Downloading {f.name}[/blue]", total=f.get_filesize(False))
                        for current_size in f.download(path, header=self.header):
                            progress.update(task_id, completed=int(current_size))
                        download_correct = f.validate()
                        if download_correct:
                            if f.do_extract and post_process:
                                # Post processing
                                progress.update(task_id, description=f"[yellow]Processing {f.name}[/yellow]")
                                process_result = f.process()
                                
                                # Removing only if processing succeeded
                                remove_result = False
                                if process_result and remove_after_pp:
                                    progress.update(task_id, description=f"[red]Removing {f.name}[/red]")
                                    remove_result = f.remove()
                                
                                # Final status in the same line
                                if process_result and remove_result:
                                    status = f"[green]✓ {f.name} (processed & removed)[/green]"
                                elif process_result:
                                    status = f"[yellow]⚠ {f.name} (processed, removal failed)[/yellow]"
                                elif remove_result:
                                    status = f"[yellow]⚠ {f.name} (processed failed, removed)[/yellow]"
                                else:
                                    status = f"[red]✗ {f.name} (processed & removal failed)[/red]"
                                
                                progress.update(task_id, description=status, completed=f.get_filesize(False))
                            else:
                                status = f"[green]✓ {f.name}[/green]"
                                progress.update(task_id, description=status, complected=f.get_filesize(False))
                        else:
                            status = f"[red]✗ {f.name} (wrong hash value)[/red]"
            else:
                print(f"No files to download.")
        else:
            print("Download aborted.")
