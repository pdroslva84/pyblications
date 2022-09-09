# pyblications

A tool to help me keep my list of publications (in BibTeX format) up to date.

The main functions are:
- add an entry to the database based on DOI
- export the whole database as a formatted bibliography

## Installation

Clone this repo, change into folder, and create environment and install dependencies with:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```
usage: pyblications.py [-h] {add,export} ...

Manage a .bib database.

positional arguments:
  {add,export}
    add         Add an entry to the databse.
    export      Export database using a citation style.

options:
  -h, --help    show this help message and exit
  ```

### add an entry

```
usage: pyblications.py add [-h] doi bib

positional arguments:
  doi         a Digital Object Identifier (DOI)
  bib         a bibliographic database file in BibTeX format (.bib)

options:
  -h, --help  show this help message and exit
```

### export database

```
usage: pyblications.py export [-h] [--style STYLE] bib

positional arguments:
  bib            a bibliographic database file in BibTeX format (.bib)

options:
  -h, --help     show this help message and exit
  --style STYLE  citation style (CSL) file (default: apa.csl)
  ```

## Considerations

The script relies on the [citeproc-py](https://github.com/brechtm/citeproc-py) library, which is currently unmaintained (https://github.com/brechtm/citeproc-py/issues/88), so it might break in the future.
