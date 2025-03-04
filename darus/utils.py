import os


def dir_exists(path: str) -> bool:
    """
    Checks if the specified directory exists. If not, asks the user to create it

    :param path: The directory path to check or create
    :type path: str
    :return: True if the directory exists or was created, False otherwise
    :rtype: bool
    """

    path_exists = True

    if not os.path.isdir(path):
        path_exists = False

        # If directory not exists, try to create it - if the user wants to.
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
                print(f"The directory '{path}' has been created.")
                path_exists = True

            except Exception as e:
                print(f"An error occurred while creating the directory: {e}")
        else:
            print("No directory created.")

    return path_exists
