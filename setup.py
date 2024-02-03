from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="account-scraper",
    version="0.0.1",
    description="library that scrapes the data from an account such as securities, bank",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hirano00o/account-scraper",
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
        "chromedriver-binary",
        "selenium",
        "pandas",
        "numpy",
    ],
    python_requires='>=3.11',
)
