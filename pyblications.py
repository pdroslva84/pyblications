import argparse
import subprocess
import sys

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
import requests

from citeproc.source.bibtex import BibTeX
from citeproc import CitationStylesStyle, CitationStylesBibliography
from citeproc import formatter
from citeproc import Citation, CitationItem

# for syntax highlight
from rich.console import Console
from rich.syntax import Syntax


#########################
### UTILITY FUNCTIONS ###
#########################

def get_response(url, headers):
    try:
        resp = requests.get(url=url, headers=headers, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except Exception as e:
        print(e)
        sys.exit(1)


def get_bib_from_doi(doi):
    url = f"https://doi.org/{doi}"
    headers = {"Accept":"application/x-bibtex"}
    bib_str = get_response(url, headers).text
    return bibtexparser.loads(bib_str)


def get_bib_from_file(bib_filename):
    with open(bib_filename, 'r') as bibtex_file:
        return bibtexparser.load(bibtex_file)


def make_database_backup(filename):
    cmd = f"cp {filename} {filename}.bak"
    return subprocess.run(cmd.split())


def write_bib(bib, filename):
    # disable sorting (default is "ID")
    writer = BibTexWriter()
    writer.order_entries_by = None
    with open(filename, 'w') as outfile:
        bibtexparser.dump(bib, outfile, writer=writer)


def user_confirm_add(args, new_bib):
    print(f"The following entry was found for {args.doi}:")

    console = Console()
    syntax = Syntax(bibtexparser.dumps(new_bib).strip(), "bibtex")
    console.print(syntax)

    while True:
        user_confirm = input(f"Do you want to add this entry to {args.bib}?\nThe database will be backed up as {args.bib}.bak before being updated. (yes/no)\n")

        if user_confirm.lower() in ['y', "yes"]:
            return
        elif user_confirm.lower() in ['n', "no"]:
            print("Aborting...")
            sys.exit(1)


def get_formatted_bib(bibfile, stylefile):
    bib_source = BibTeX(bibfile)
    bib_style = CitationStylesStyle(stylefile, validate=False)
    bibliography = CitationStylesBibliography(bib_style, bib_source, formatter.plain)

    for entry in bib_source:
        citation = Citation([CitationItem(entry)])
        bibliography.register(citation)

    f_bibliography = ''
    for item in bibliography.bibliography():
        f_bibliography += str(item) + '\n'

    return f_bibliography


############################
### SUBCOMMAND FUNCTIONS ###
############################

def add_entry_from_doi(args):
    new_bib = get_bib_from_doi(args.doi)
    db = get_bib_from_file(args.bib)

    # user has to confirm correct entry was retrieved, else abort
    user_confirm_add(args, new_bib)

    # backing up existing database (.bib.bak)
    make_database_backup(args.bib)

    # bibtexparser doesn't allow reverse sorting of entries by year
    # so the easiest way of maintaining reverse chronological order
    # is to alway insert the new entry at the beginning of the database
    # in write.bib the sorting is set to none
    db.entries.insert(0, new_bib.entries[0])
    write_bib(db, args.bib)

    print("Database successfully updated.")
    sys.exit(0)


def export_database(args):
    print(get_formatted_bib(args.bib, args.style).strip())
    sys.exit(0)


############
### MAIN ###
############

def main():

    ### ###
    ### dealing with command line args
    ### ###
    parser = argparse.ArgumentParser(description="Manage a .bib database.")
    subparsers = parser.add_subparsers()

    # add: subcommand for adding an entry based on DOI
    parser_add_entry = subparsers.add_parser("add",
                                             help="Add an entry to the databse.")

    parser_add_entry.add_argument("doi",
                                  help="a Digital Object Identifier (DOI)")

    parser_add_entry.add_argument("bib",
                                  help="a bibliographic database file in BibTeX format (.bib)")

    parser_add_entry.set_defaults(func=add_entry_from_doi)

    # export: subcommand for exporting the database in a particular citation style
    parser_export = subparsers.add_parser("export",
                                          help="Export database using a citation style.",
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser_export.add_argument("--style",
                               help="citation style (CSL) file",
                               default="apa.csl")

    parser_export.add_argument("bib",
                               help="a bibliographic database file in BibTeX format (.bib)")

    parser_export.set_defaults(func=export_database)

    # parsing args
    args = parser.parse_args()

    # if no args were given print usage (not printed by default because top parser has no args) and exit
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    ### ###
    ### call the respective functions for the selected subcommands
    ### ###
    args.func(args)


if __name__ == "__main__":
    main()
