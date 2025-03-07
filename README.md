# DaRUS Dataset Downloader

A Python package for easily downloading datasets from the DaRUS (DataRepository of the University of Stuttgart) platform.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Download Specific Files](#download-specific-files)
  - [Private Datasets](#private-datasets)
- [License](#license)
- [Contributing](#contributing)
- [Additional Resources](#additional-resources)
- [Detailed Documentation](#detailed-documentation)

## Overview

This package provides a simple interface to download complete datasets or specific files from DaRUS repositories like [FEM Dataset](https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801). It handles authentication, file filtering, and download management.

## Installation

Install directly from GitHub using pip:

```bash
pip install git+https://github.com/baumsebastian/darus.git
```


## Usage

The package can be configured with the following parameters:

| Parameter | Description |
|-----------|-------------|
| url | The DARUS dataset URL | 
| path | Local directory where downloaded files will be stored |
| files | List of specific files to download (if empty, all files will be downloaded) \[Default: empty list \[ \]\]|
| api_token | Authentication token for restricted datasets \[Default:`None`\]|

All examples below use this sample dataset:
```
https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801
```

### Basic Usage

Download an entire dataset:

```python
from darus import Downloader 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./my_dataset"

# Download the complete dataset
dl = Downloader(url)
dl.start_download(path)
```

**Note:** Every file has a value _directory_ in its metadata (see [Add a File to Dataset](https://guides.dataverse.org/en/6.5/api/native-api.html#id90)). `Downloader` creates and stores the downloaded file in the specific _directory_ according to `path/directory`.

### Download Specific Files

Download only selected files from a dataset:

```python
from darus import Downloader 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
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

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
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
