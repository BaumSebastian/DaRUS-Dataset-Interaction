from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="darus",
    version="0.3.0",  # Added CLI interface and improved configuration
    author="Sebastian Baum",
    description="Download datasets from DaRUS (DataRepository of the University of Stuttgart)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BaumSebastian/DaRUS-Dataset-Interaction",
    packages=find_packages(),
    license="GPL-3.0",
    python_requires=">=3.8",
    keywords=["dataverse", "darus", "dataset", "download", "research-data", "stuttgart"],
    project_urls={
        "Bug Reports": "https://github.com/BaumSebastian/DaRUS-Dataset-Interaction/issues",
        "Source": "https://github.com/BaumSebastian/DaRUS-Dataset-Interaction",
        "Documentation": "https://github.com/BaumSebastian/DaRUS-Dataset-Interaction#readme",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=[
        "requests>=2.25.0",  # Added version constraints for better compatibility
        "validators>=0.18.0",
        "humanize>=3.0.0",
        "rich>=10.0.0",
        "pyyaml>=5.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "responses>=0.23.0",
            "black>=23.0.0",
        ]
    },
    zip_safe=False,  # Ensures proper installation
)
