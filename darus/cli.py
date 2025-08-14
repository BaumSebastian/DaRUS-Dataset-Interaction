import argparse
import yaml
from pathlib import Path

from . import Dataset
from .utils import setup_logging


def main():
    """Main CLI entry point for darus-download command."""
    # Setup logging
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Download datasets from DaRUS")

    parser.add_argument(
        "--config", "-c", help="Config file path (optional)"
    )
    parser.add_argument("--url", "-u", help="Dataset URL")
    parser.add_argument("--path", "-p", help="Download path")
    parser.add_argument("--token", "-t", help="API token")
    parser.add_argument("--files", "-f", nargs="*", help="Specific files to download")

    args = parser.parse_args()

    # Load config file if provided and exists
    config = {}
    if args.config and Path(args.config).exists():
        with open(args.config) as config_file:
            config = yaml.safe_load(config_file.read()) or {}

    # Override with CLI arguments if provided
    url = args.url or config.get("url")
    path = args.path or config.get("path", "./data")
    api_token = args.token or config.get("api_token")
    files = args.files if args.files is not None else config.get("files")

    if not url:
        parser.error("URL is required. Provide it via --url or in config file.")

    # Create dataset and download
    dl = Dataset(url, api_token=api_token if api_token else None)
    dl.summary()
    dl.download(path, files=files)


if __name__ == "__main__":
    main()