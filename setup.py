from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.14'
DESCRIPTION = 'Restful-genie, package to deliver REST API for LongevityGPT'
LONG_DESCRIPTION = 'Restful-genie, package to deliver REST API for LongevityGPT'

# Setting up
setup(
    name="longevity-gpts",
    version=VERSION,
    author="karmazinalex (Karmazin Alex)",
    author_email="<karmazinalex@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pycomfort', 'click', 'gspread', "polars", "indexpaper>=0.0.15", "pydantic==1.10.12", 'hybrid_search'],
    keywords=['python', 'llm', 'science', 'review', 'spreadsheets'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)