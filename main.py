import argparse
import yaml
from pathlib import Path

from darus import Dataset
from darus.utils import setup_logging


def main():
    # Setup logging
    setup_logging()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    default_config = script_dir / "config.yaml"

    parser = argparse.ArgumentParser(description="Download datasets from DaRUS")

    parser.add_argument(
        "--config", "-c", default=str(default_config), help="Config file path"
    )
    parser.add_argument("--url", "-u", help="Dataset URL")
    parser.add_argument("--path", "-p", help="Download path")
    parser.add_argument("--token", "-t", help="API token")
    parser.add_argument("--files", "-f", nargs="*", help="Specific files to download")

    args = parser.parse_args()

    # Load config file
    with open(args.config) as config_file:
        config = yaml.safe_load(config_file.read())

    # Override with CLI arguments if provided
    url = args.url or config["url"]
    path = args.path or config["path"]
    api_token = args.token or config["api_token"]
    files = args.files if args.files is not None else config["files"]

    # Create dataset and download
    dl = Dataset(url, api_token=api_token if api_token else None)
    dl.summary()
    dl.download(path, files=files)


if __name__ == "__main__":
    main()
