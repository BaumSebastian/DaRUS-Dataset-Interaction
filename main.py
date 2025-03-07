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

    # Load Config
    PATH = config["PATH"]
    FILES = config["FILES"]
    URL = config["URL"]
    API_TOKEN = config["API_TOKEN"]

    dl = Downloader(URL, files=FILES, api_token=API_TOKEN)
    dl.start_download(PATH)

    print("Download finished.")


if __name__ == "__main__":
    main()
