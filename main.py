import validators
import os
import requests
import yaml
import json

# Custom imports
from darus import Downloader

def main():

    CONFIG_FILE = "config.yaml"

    with open(CONFIG_FILE) as cf_file:
        config = yaml.safe_load(cf_file.read())

    PATH = config["PATH"]
    FILES = config["FILES"]
    SERVER_URL = config["SERVER_URL"]
    PERSISTENT_IDENTIFIER = config["PERSISTENT_IDENTIFIER"]
    URL = (
        f"{SERVER_URL}/api/datasets/:persistentId/?persistentId={PERSISTENT_IDENTIFIER}"
    )

    # Add API token if needed for authentification.
    API_TOKEN = config['API_TOKEN']
    HEADER = {"X-Dataverse-key": API_TOKEN} if API_TOKEN else None

    dl = Downloader(URL, HEADER, FILES)
    dl.start_download(PATH)

if __name__ == "__main__":
    main()
