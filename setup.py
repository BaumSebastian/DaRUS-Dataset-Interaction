from setuptools import setup, find_packages

setup(
    name="darus",
    version="0.0.1",
    description="Basic interaction with DaRUS",
    url="https://github.com/BaumSebastian/DaRUS-data-downloader",
    author="Sebastian Baum",
    license="GNUv3",
    packages=["darus"],
    zip_safe=False,
    install_requires=['requests', 'validators', 'humanize', 'tqdm', 'pyyaml'],
)
