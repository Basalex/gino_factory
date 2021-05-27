import os
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open("README.rst", "r", encoding="utf-8") as f:
    long_description = f.read()

VERSION = '0.1.0'
DESCRIPTION = 'Gino Factory'
LONG_DESCRIPTION = 'Generate random data for testing'

# Setting up
setup(
    name="gino-factory",
    version=VERSION,
    author="Basalex (Alexander Baskakov)",
    author_email="<alexanderbaskakov@mail.ru>",
    description=DESCRIPTION,
    long_description=long_description,
    packages=find_packages(),
    install_requires=['gino', 'faker'],
    keywords=['python', 'gino', 'faker'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    project_urls={
        "Source": "https://github.com/Basalex/gino_factory",
    },
)
