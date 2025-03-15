import os


def dir_exists(path: str) -> bool:
    """
    Checks if the specified directory exists. If not, asks the user to create it.

    :param path: The path to the directory to check or create.
    :type path: str
    :return: True if the directory exists or was created, False otherwise.
    :rtype: bool
    """

    path_exists = os.path.isdir(path)

    if not path_exists:
        create = (
            input(
                f"The directory '{path}' does not exist.\nWould you like to create it? (yes[y]/no[n]): "
            )
            .strip()
            .lower()
        )

        if create in ["yes", "y"]:
            try:
                os.makedirs(path)
            except Exception as e:
                print(f"An error occurred while creating the directory: {e}")
            else:
                path_exists = os.path.isdir(path)

    return path_exists
