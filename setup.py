from setuptools import setup

setup(
    name="darus",
    version="0.1.0",
    author="Sebastian Baum",
    description="Basic interaction with DaRUS",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/BaumSebastian/DaRUS-Dataset-Interaction",
    packages=["darus"],
    license="GNU",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "validators", "humanize", "rich", "pyyaml"],
)
