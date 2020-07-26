# PyPaperDB -- A Python based BibTeX manager.

PyPaperDB provides a QT gui [BiBTeX](http://www.bibtex.org/) manager.
The database is stored in xml format. The BibTeX data can be exported to a .bib file which excludes custom user metadata, such as tags, summaries and PDF files.

Features:

* Data stored in XML database
* Supports user summaries that are excluded from generated BibTeX files
* BibTeX files can be generated on demand from a subset of entries in the database
* Locally stored PDF files can be linked to a database entry.
* CLI interface.


Future planned features:

* GUI option menu to configure topics and entry types
* GUI configuration

## Installation

`pip install --upgrade pypaperdb`

To customize the location of the database file and to set the directory in which the PDF files are stored

`cp pypaperdb_default.cfg ~/.pypaperdb/pypaperdb.cfg`

and edit the configuration as needed.

## Usage

When adding a new entry, the data can be parsed automatically from the BibTeX string when pasted into the BibTeX field.

Unicode characters can be used in the "Extra" field of "New entry", but not all characters are yet recognised.

Months are internally parsed to ensure a uniform output.

CLI options are available by typing

`pypaperdb --help`


## Credits
Icon made by [Smashicons](https://www.flaticon.com/authors/smashicons) from [Flaticon](https://www.flaticon.com).
