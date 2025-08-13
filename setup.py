# Create this temporarily to test dependency installation
from setuptools import setup, find_packages

# Print what packages are found
print("Found packages:", find_packages())

setup(
    name="darus",
    version="0.2.0",
    author="Sebastian Baum", 
    description="Basic interaction with DaRUS",
    url="https://github.com/BaumSebastian/DaRUS-Dataset-Interaction",
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests>=2.25.0",  # Added version constraints for better compatibility
        "validators>=0.18.0",
        "humanize>=3.0.0",
        "rich>=10.0.0", 
        "pyyaml>=5.4.0"
    ],
    zip_safe=False,  # Ensures proper installation
)