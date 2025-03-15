from pathlib import Path


def dir_exists(path: str) -> bool:
    """
    Checks if the specified directory exists. If not, asks the user to create it.

    :param path: The path to the directory to check or create.
    :type path: str
    :return: True if the directory exists or was created, False otherwise.
    :rtype: bool
    """

    path_obj = Path(path).resolve()

    try:
        path_is_existing_dir = path_obj.is_dir()
    except PermissionError as pe:
        print(pe)
        return False
    except Exception as e:
        print(
            f"An error occured while trying to check if '{path_obj}' is a valid directory. {e}"
        )
        return False

    if path_is_existing_dir:
        return True

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
        except Exception as e:
            print(f"An error occurred while creating the directory: {e}")

    return path_obj.is_dir()
