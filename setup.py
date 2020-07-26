from setuptools import setup, find_packages
import pathlib


import pypaperdb
here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')


required_packages = ['bibtexentryparser','xmldb','lxml','pyperclip','PyQt5',]

setup(
    name='pypaperdb',
    version=pypaperdb.__version__,
    description='A Python BibTeX manager',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author=pypaperdb.__authors__,
    author_email=pypaperdb.__author_emails__,
    url='',
    license= 'GPLv3',
    packages=find_packages(where=here),
    install_requires=[],
    python_requires='>=3',
    platforms=['any']
)
