import validators
import os
import requests
import yaml
import json

from darus import Dataset

def main():

    config_file_path = "./config/config_template.yaml"

    with open(config_file_path) as config_file:
        config = yaml.safe_load(config_file.read())

    path = config["path"]
    files = config["files"]
    url = config["url"]
    api_token = config["api_token"]

    dl = Dataset(url, api_token=api_token)
    dl.summary()
    dl.download(path, files=files)

if __name__ == "__main__":
  main()
