import validators
import os
import requests
import yaml
import json

# Custom imports
from darus import Dataset


def main():

    CONFIG_FILE = "config.example.yaml"

    with open(CONFIG_FILE) as cf_file:
        config = yaml.safe_load(cf_file.read())

    # Load Config
    PATH = config["PATH"]
    FILES = config["FILES"]
    URL = config["URL"]
    API_TOKEN = config["API_TOKEN"]

    dl = Dataset(URL, files=FILES, api_token=API_TOKEN)
    dl.summary()
    dl.download(PATH)

if __name__ == "__main__":
    main()
