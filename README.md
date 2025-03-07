# DaRUS Dataset Downloader

A Python package for easily downloading datasets from the DaRUS (DataRepository of the University of Stuttgart) platform.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Download Specific Files](#download-specific-files)
  - [Private Datasets](#private-datasets)
- [License](#license)
- [Contributing](#contributing)
- [Additional Resources](#additional-resources)
- [Detailed Documentation](#detailed-documentation)

## Overview

This package provides a simple interface to download complete datasets or specific files from DaRUS repositories like [FEM Dataset](https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353). It handles authentication, file filtering, and download management.

## Installation

Install directly from GitHub using pip:

```bash
pip install git+https://github.com/baumsebastian/darus.git
```

## Configuration

The package can be configured with the following parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| path | Local directory where downloaded files will be stored | Required |
| url | The DARUS dataset URL | Required |
| files | List of specific files to download (if empty, all files will be downloaded) | [] |
| api_token | Authentication token for restricted datasets | None |

## Usage

All examples below use this sample dataset:
```
https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353
```

### Basic Usage

Download an entire dataset:

```python
from darus import Downloader 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353"
path = "./my_dataset"

# Download the complete dataset
dl = Downloader(url)
dl.start_download(path)
```

**Note:** DaRUS allows that every file has a 'directory' stored as metadata ([Add a File to Dataset](https://guides.dataverse.org/en/6.5/api/native-api.html#id90)). This package creates and stores the data in the specific directory to 'path/subdir'.

### Download Specific Files

Download only selected files from a dataset:

```python
from darus import Downloader 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353"
path = "./my_dataset"

# Download only 'metadata.tab' 
files = ["metadata.tab"]

dl = Downloader(url, files=files)
dl.start_download(path)
```

**Note:** DaRUS converts tabular data like .csv files into .tab format. This package downloads the original file format (e.g., .csv) when available.

### Private Datasets

For datasets that require authentication:

```python
from darus import Downloader 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4353"
path = "./my_dataset"

# API token for accessing private datasets
token = 'xxxx-xxxx-xxxx-xxxx'

dl = Downloader(url, api_token=token)
dl.start_download(path)
```

## License

[GNU V3](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Additional Resources

- [Dataverse API Guide](https://guides.dataverse.org/en/latest/api/index.html) - Detailed explanation of the underlying API
- [Alternative Implementation](https://github.com/iswunistuttgart/darus_data_download) - Another repository for downloading DaRUS data

## Detailed Documentation

*Under Construction*

This section will contain detailed documentation about advanced usage of the package.
