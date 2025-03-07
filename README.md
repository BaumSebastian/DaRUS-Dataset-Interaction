# DARUS Dataset Downloader

A Python package for easily downloading datasets from the DARUS (DAtarepository of the University of Stuttgart) platform.

## Overview

This package provides a simple interface to download complete datasets or specific files from DARUS repositories like https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353. It handles authentication, file filtering, and download management.

## Installation

Install directly from GitHub using pip:

```bash
pip install git+https://github.com/username/darus-downloader.git
```

## Configuration

The package can be configured with the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| PATH | Local directory where downloaded files will be stored | Current directory |
| FILES | List of specific files to download (if empty, all files will be downloaded) | [] |
| API_TOKEN | Authentication token for restricted datasets | None |
| URL | The DARUS dataset URL | Required |

## Usage

### Basic Usage

```python
from darus import Downloader 

url ="https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353"
path="./my_dataset"

# Download an entire dataset
dl = Downloader(url, path)
dl.start()
```

### Download Specific Files

```python
from darus import Downloader 

url ="https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353"
path="./my_dataset"

# Download an entire dataset
dl = Downloader(
url, path,
    files=["data.csv", "metadata.json"]
    )
dl.start()
```

### Private Datasets

For datasets that require authentication:

```python
from darus import Downloader 

url ="https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353"
path="./my_dataset"

# Download an entire dataset
dl = Downloader(
        url, path,
        files=["data.csv", "metadata.json"]
        api_token='xxxx-xxxx-xxxx-xxxx'
        )
dl.start()
```

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Other sources

There are other repositories, that support basic interaction as well like:
Also have a look at the documentation of the darus here:

## Detailed Explanation

This section is about a detailed explanation how to interact with the downloader.
It is also a guide for publishers to may discover good benefits.
