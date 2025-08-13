# DaRUS Dataset Interaction

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-green.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python package for easily downloading datasets from the [DaRUS](https://darus.uni-stuttgart.de/) (DataRepository of the University of Stuttgart) platform. 
Currently the web interface of darus limits the size of downloads by 2 GB, which makes it hard to download big datasets like the [FEM Dataset](https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801) example below. This package enables interaction with the dataset by downloading the whole dataset (or [specific files](#download-specific-files)), handles authentication and directory management.

## Table of Contents
- [DaRUS Dataset Interaction](#darus-dataset-interaction)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
    - [Quick Install (Recommended)](#quick-install-recommended)
    - [From Source](#from-source)
    - [Development Setup](#development-setup)
  - [Python API Usage](#python-api-usage)
    - [Basic Usage](#basic-usage)
    - [Download Specific Files](#download-specific-files)
    - [Private Datasets](#private-datasets)
    - [Post Processing](#post-processing)
    - [Sample Output](#sample-output)
  - [CLI Usage (for developers)](#cli-usage-for-developers)
  - [License](#license)
  - [Contributing](#contributing)
  - [Additional Resources](#additional-resources)

## Installation

### Quick Install (Recommended)

```bash
# Using pip
pip install git+https://github.com/BaumSebastian/DaRUS-Dataset-Interaction.git

# Using uv (faster) - https://github.com/astral-sh/uv
uv pip install git+https://github.com/BaumSebastian/DaRUS-Dataset-Interaction.git
```

### From Source

```bash
git clone https://github.com/BaumSebastian/DaRUS-Dataset-Interaction.git
cd DaRUS-Dataset-Interaction
pip install .
```

### Development Setup

```bash
git clone https://github.com/BaumSebastian/DaRUS-Dataset-Interaction.git
cd DaRUS-Dataset-Interaction
pip install -e .[dev]  # Includes testing tools
```

## Python API Usage

### Basic Usage

Download an entire dataset:

```python
from darus import Dataset 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./data"

# Download the complete dataset
ds = Dataset(url)
ds.download(path)
```

**Note:** Every file has a value _directory_ in its metadata (see [Add a File to Dataset](https://guides.dataverse.org/en/6.5/api/native-api.html#id90)). `Dataset` creates and stores the downloaded file in the specific _directory_ according to `path/directory`.



### Download Specific Files

Download only selected files (`["metadata.tab"]`) from a dataset:

```python
from darus import Dataset 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./data"

files = ["metadata.tab"] 

ds = Dataset(url)
ds.download(path, files=files)
```

**Note:** DaRUS converts tabular data like .csv files into .tab format. This package downloads the original file format (e.g., .csv) when available.

### Private Datasets

For datasets that require authentication use the `api_token` of your DaRUS account.

```python
from darus import Dataset 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./data"

api_token = 'xxxx-xxxx-xxxx-xxxx'

ds = Dataset(url, api_token=api_token)
ds.download(path)
```
### Post Processing 

The method `download` of `Dataset` accepts two optional arguments.
- `post_process` : Zip archieves are automatically extracted, after download completed. Default: `True`.
- `remove_after_pp`: The Zip archieves are deleted after extration. Default: `True`.

### Sample Output

Executing following script, results in the output below. 

```python
from darus import Dataset 

url = "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801"
path = "./data"

ds = Dataset(url)
ds.summary()
ds.download(path)
```
**Note:** The _Dataset Summary_ and _Files in Dataset_ is only printed, when `ds.summary()` is called.

The output looks like following:
``` bash
Dataset Summary
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property      ┃ Value                                                                             ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ URL           │ https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801 │
│ Persistent ID │ doi:10.18419/DARUS-4801                                                           │
│ Last Update   │ 2025-03-12 12:32:17                                                               │
│ License       │ CC BY 4.0                                                                         │
└───────────────┴───────────────────────────────────────────────────────────────────────────────────┘
Files in Dataset
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name              ┃ Size    ┃ Original Available ┃ Description                                                 ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 113525_116825.zip │ 59.2 GB │                    │ Contains all simulations with ID between 113525 and 116825. │
│ 116826_211007.zip │ 59.2 GB │                    │ Contains all simulations with ID between 116826 and 211007. │
│ 16039_19338.zip   │ 59.2 GB │                    │ Contains all simulations with ID between 16039 and 19338.   │
│ 19339_113524.zip  │ 59.1 GB │                    │ Contains all simulations with ID between 19339 and 113524.  │
│ 257076_260375.zip │ 59.7 GB │                    │ Contains all simulations with ID between 257076 and 260375. │
│ 260376_306443.zip │ 59.8 GB │                    │ Contains all simulations with ID between 260376 and 306443. │
│ 306444_309743.zip │ 59.7 GB │                    │ Contains all simulations with ID between 306444 and 309743. │
│ 309744_403925.zip │ 59.6 GB │                    │ Contains all simulations with ID between 309744 and 403925. │
│ 403926_406296.zip │ 42.6 GB │                    │ Contains all simulations with ID between 403926 and 406296. │
│ metadata.tab      │ 2.5 MB  │ ✓(metadata.csv)    │ Metadata of the simulations.                                │
└───────────────────┴─────────┴────────────────────┴─────────────────────────────────────────────────────────────┘
Downloading...
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name              ┃ Size    ┃ Directory  ┃ Download Original ┃ Description                                                 ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 113525_116825.zip │ 59.2 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 113525 and 116825. │
│ 116826_211007.zip │ 59.2 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 116826 and 211007. │
│ 16039_19338.zip   │ 59.2 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 16039 and 19338.   │
│ 19339_113524.zip  │ 59.1 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 19339 and 113524.  │
│ 257076_260375.zip │ 59.7 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 257076 and 260375. │
│ 260376_306443.zip │ 59.8 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 260376 and 306443. │
│ 306444_309743.zip │ 59.7 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 306444 and 309743. │
│ 309744_403925.zip │ 59.6 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 309744 and 403925. │
│ 403926_406296.zip │ 42.6 GB │ .\data\h5\ │                   │ Contains all simulations with ID between 403926 and 406296. │
│ metadata.tab      │ 2.5 MB  │ .\data\    │ ✓(metadata.csv)   │ Metadata of the simulations.                                │
└───────────────────┴─────────┴────────────┴───────────────────┴─────────────────────────────────────────────────────────────┘
Downloading 113525_116825.zip ━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.9% • 5.2/59.2 GB • 0:08:07 • 1:22:43 • 10.9 MB/s
....
```

## CLI Usage (for developers)

If you cloned the repository, you can use the command line interface:

```bash
# Basic usage with default config
python main.py

# Override specific settings
python main.py --url "https://darus.uni-stuttgart.de/dataset.xhtml?persistentId=doi:10.18419/DARUS-4801" --path "./downloads"

# Use custom config file
python main.py --config config_private.yaml

# Download specific files only
python main.py --files metadata.csv data.zip

# Private datasets with API token
python main.py --token "your-api-token"

# Combine multiple arguments
python main.py --path "/your/download/path" --token "your-token" --files metadata.csv
```

**Available Arguments:**
- `--config, -c`: Config file path (default: `config.yaml`)
- `--url, -u`: Dataset URL
- `--path, -p`: Download directory path
- `--token, -t`: API token for authentication
- `--files, -f`: Specific files to download (space-separated)
- `--help`: Show help message

## License

[GNU V3](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Additional Resources

- [Dataverse API Guide](https://guides.dataverse.org/en/latest/api/index.html) - Detailed explanation of the underlying API
- [Alternative Implementation](https://github.com/iswunistuttgart/darus_data_download) - Another repository for downloading DaRUS data
