from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="acctf",
    version="0.5.2",
    description="library that scrapes the data from an account such as securities, bank",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hirano00o/acctf",
    author="hirano00o",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="scrape, account, development",
    packages=find_packages(),
    install_requires=[
        "beautifulsoup4",
        "bs4",
        "selenium",
        "pandas",
        "lxml",
        "PySocks",
        "pyotp",
        "html5lib",
    ],
    python_requires='>=3.11',
)
