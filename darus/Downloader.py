from .DatasetFile import DatasetFile

class Downloader():
    def __init__(self, server_url:str):
        self.server_url = server_url
        self.files = files
        self.persistent_identifier = persistent_identifier
        self.url = (
            f"{SERVER_URL}/api/datasets/:persistentId/?persistentId={PERSISTENT_IDENTIFIER}"
                )

    def config(self, FILES):
        pass

    def _validate(self):
        pass

    def start(path:str):

        CONFIG_FILE = "config.yaml"

        with open(CONFIG_FILE) as cf_file:
            config = yaml.safe_load(cf_file.read())

        PATH = config["PATH"]
        FILES = config["FILES"]
        SERVER_URL = config["SERVER_URL"]
        PERSISTENT_IDENTIFIER = config["PERSISTENT_IDENTIFIER"]
        URL = (
            f"{SERVER_URL}/api/datasets/:persistentId/?persistentId={PERSISTENT_IDENTIFIER}"
        )

        if not validators.url(URL):
            raise ValueError(
                f"The provided url {URL} is not valid.\nPlease check your config ({CONFIG_FILE})."
            )

        # Add API token if needed for authentification.
        header = None
        API_TOKEN = config["API_TOKEN"]

        if API_TOKEN:
            header = {"X-Dataverse-key": API_TOKEN}

        if dir_exists(PATH):
            try:
                r = requests.get(URL, headers=header)
                r.raise_for_status()

                if r.ok:

                    json_response = json.loads(r.text)["data"]["latestVersion"]["files"]
                    dataset_files = list(
                        map(
                            lambda item_info: DatasetFile(
                                item_info["dataFile"], SERVER_URL
                            ),
                            json_response,
                        )
                    )

                    message = "Downloading:"

                    # Check if user wants to download only specific dataset_files
                    if FILES:
                        dataset_files = [f for f in dataset_files if f.name in FILES]

                        if len(dataset_files) != len(FILES):
                            raise ValueError(
                                f"Could not find all files from config ({FILES}) in response.\nPlease check your config ({CONFIG_FILE})."
                            )
                        message = (
                            'Downloading custom set of files (see "FILES" config):'
                        )

                    print(f'\n{message}\n{len(message)* "-"}')
                    print(
                        *map(
                            lambda file: f"-{file.name} [{file.get_dataset_filesize()}]",
                            dataset_files,
                        ),'\n',
                        sep="\n",
                    )

                    if len(dataset_files) > 0:
                        for f in dataset_files:
                            successful = f.download(path=PATH, header=header)
                            if successful:
                                print(
                                    f"Download '{f.name}' successful (hash: {f.get_hash()})"
                                )
                            else:
                                print(f"Error while trying to download {f.name}")
                    else:
                        print(f"No files to download.")
                else:
                    print(f"Error while trying to download.\n{r.reason}")

            except requests.exceptions.HTTPError as err:
                print("Error while trying to download.")
                print(err)
