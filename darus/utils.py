import logging
from pathlib import Path


def setup_logging(level=logging.INFO):
    """
    Configure logging for the darus package.

    :param level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def get_logger(name: str):
    """
    Get a logger instance for the given name.

    :param name: Logger name (typically __name__)
    :return: Logger instance
    """
    return logging.getLogger(name)


def dir_exists(path: str, interactive: bool = True) -> bool:
    """
    Checks if the specified directory exists. If not, asks the user to create it.

    :param path: The path to the directory to check or create.
    :type path: str
    :param interactive: Whether to prompt user for directory creation (default: True)
    :type interactive: bool
    :return: True if the directory exists or was created, False otherwise.
    :rtype: bool
    """
    logger = get_logger(__name__)
    path_obj = Path(path).resolve()

    try:
        path_is_existing_dir = path_obj.is_dir()
    except PermissionError as pe:
        logger.error(f"Permission denied accessing directory '{path_obj}': {pe}")
        return False
    except Exception as e:
        logger.error(
            f"An error occurred while trying to check if '{path_obj}' is a valid directory: {e}"
        )
        return False

    if path_is_existing_dir:
        return True

    if not interactive:
        logger.warning(
            f"Directory '{path_obj}' does not exist and interactive mode is disabled"
        )
        return False

    create_directory = (
        input(
            f"The directory '{path_obj}' does not exist.\nWould you like to create it? (yes[y]/no[n]): "
        )
        .strip()
        .lower()
    ) in ["yes", "y"]

    if create_directory:
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {path_obj}")
        except Exception as e:
            logger.error(f"An error occurred while creating the directory: {e}")

    return path_obj.is_dir()
