from setuptools import setup, find_packages

setup(
    name="darus",
    version="0.0.1",
    description="Basic interaction with DaRUS",
    url="https://github.com/BaumSebastian/DaRUS-Dataset-Interaction",
    author="Sebastian Baum",
    license="GNU",
    packages=["darus"],
    zip_safe=False,
    install_requires=["requests", "validators", "humanize", "rich", "pyyaml"],
)
