# DaRUS Dataset Interaction

A Python package for easily downloading datasets from the ![DaRUS](https://darus.uni-stuttgart.de/) (DataRepository of the University of Stuttgart) platform.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Download Specific Files](#download-specific-files)
  - [Private Datasets](#private-datasets)
  - [Post Processing](#post-processingdeletion)
  - [Sample Output](#sample-output)
- [License](#license)
- [Contributing](#contributing)
- [Additional Resources](#additional-resources)

## Overview

This package provides a simple interface to download complete datasets or specific files from DaRUS repositories like [FEM Dataset](https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801). It handses authentication, file filtering, and download management.

## Installation

Install directly from GitHub using pip:

```bash
pip install git+https://github.com/baumsebastian/darus.git
```


## Usage

The package can be configured with the following parameters:

| Parameter | Description | Default |
|-|-|-|
| url | The DARUS dataset URL | Required |
| path | Local directory where downloaded files will be stored |Required |
| files | List of specific files to download (if empty list, all files will be downloaded) | `[ ]`|
| api_token | Authentication token for restricted datasets |`None`|

All examples below use this sample dataset:
```
https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801
```

### Basic Usage


Download an entire dataset:

```python
from darus import Dataset 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./my_dataset"

# Download the complete dataset
ds = Dataset(url)
ds.download(path)
```

**Note:** Every file has a value _directory_ in its metadata (see [Add a File to Dataset](https://guides.dataverse.org/en/6.5/api/native-api.html#id90)). `Dataset` creates and stores the downloaded file in the specific _directory_ according to `path/directory`.



### Download Specific Files

Download only selected files from a dataset:

```python
from darus import Dataset 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./my_dataset"

# Download only 'metadata.tab' 
files = ["metadata.tab"]

ds = Dataset(url, files=files)
ds.download(path)
```

**Note:** DaRUS converts tabular data like .csv files into .tab format. This package downloads the original file format (e.g., .csv) when available.

### Private Datasets

For datasets that require authentication:

```python
from darus import Dataset 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./my_dataset"

# API token for accessing private datasets
token = 'xxxx-xxxx-xxxx-xxxx'

ds = Dataset(url, api_token=token)
ds.download(path)
```
### Post Processing 

The method `download` of `Dataset` accepts two additional arguments.
- `post_process` : Zip archieves are automatically extracted, after download completed. Default: `True`.
- `remove_after_pp`: The Zip archieves are deleted after extration. Default: `True`.

### Sample Output

Executing following script, results in the output below. 

```python
from darus import Dataset 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./my_dataset"

# Download the complete dataset
ds = Dataset(url)
ds.summary()
ds.download(path)
```
**Note:** The summary is only printed, when `ds.summary()` is called.

The output looks like following:
```bash
Dataset Summary
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property      ┃ Value                                                                             ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ URL           │ https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801 │
│ Persistent ID │ doi:10.18419/DARUS-4801                                                           │
│ Last Update   │ 2025-03-07 22:56:30                                                               │
│ License       │ CC BY 4.0                                                                         │
└───────────────┴───────────────────────────────────────────────────────────────────────────────────┘
Downloading...
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name              ┃ Size    ┃ Directory           ┃ Download Original ┃ Description                                                 ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 113525_116825.zip │ 59.2 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 113525 and 116825. │
│ 116826_211007.zip │ 59.2 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 116826 and 211007. │
│ 16039_19338.zip   │ 59.2 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 16039 and 19338.   │
│ 19339_113524.zip  │ 59.1 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 19339 and 113524.  │
│ 257076_260375.zip │ 59.7 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 257076 and 260375. │
│ 260376_306443.zip │ 59.8 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 260376 and 306443. │
│ 306444_309743.zip │ 59.7 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 306444 and 309743. │
│ 309744_403925.zip │ 59.6 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 309744 and 403925. │
│ 403926_406296.zip │ 42.6 GB │ .\my_dataset\data   │                   │ Contains all simulations with ID between 403926 and 406296. │
│ metadata.tab      │ 2.5 MB  │ .\my_dataset\       │ ✓(metadata.csv)   │ Metadata of the simulations.                                │
└───────────────────┴─────────┴─────────────────────┴───────────────────┴─────────────────────────────────────────────────────────────┘
Downloading 113525_116825.zip ━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.9% • 5.2/59.2 GB • 0:08:07 • 1:22:43 • 10.9 MB/s
....
```
## License

[GNU V3](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Additional Resources

- [Dataverse API Guide](https://guides.dataverse.org/en/latest/api/index.html) - Detailed explanation of the underlying API
- [Alternative Implementation](https://github.com/iswunistuttgart/darus_data_download) - Another repository for downloading DaRUS data
