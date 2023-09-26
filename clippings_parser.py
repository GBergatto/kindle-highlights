#! /usr/bin/python

import os
import re
import sys

LEN = int(sys.argv[1])
SEPARATOR = "==========\n"
OUT_DIR = "out"
ANKI_FILE = "anki.txt"

title_re = re.compile("^(.*)\((.*)\)$")
meta_re = re.compile("^-\s*Your (\S+) (.*)Added on\s+(.+)$")
pos_re = re.compile("Location (\d+)(?:-(\d+)|)")


def parse_my_clippings():
    books = dict()

    with open("My Clippings.txt", mode="r", encoding="utf-8-sig") as cf:
        clippings = cf.read().split(SEPARATOR)[:-1]

        for c in clippings:
            split_c = c.split("\n")
            title_line = split_c[0]
            meta_line = split_c[1]
            # the 3rd and last elements of the list are empty strings
            body = "\n".join(split_c[3:-1])

            # parse title, subtitle and author
            title_match = re.match(title_re, title_line) 
            if not title_match:
                # TODO: log error to a log file
                continue

            full_title, author = title_match.groups()
            full_title = full_title.strip().strip("\ufeff")
            ft_split = full_title.split(":")
            title = ft_split[0]
            subtitle = ""
            if (len(ft_split)>1):
                subtitle = ft_split[1].strip()

            # parse type, position and date
            meta_match = re.match(meta_re, meta_line)
            if not meta_match:
                # TODO: log error to a log file
                continue

            # date is not used
            ctype, pos, _ = meta_match.groups()
            ctype = ctype.lower()

            if ctype == "bookmark":
                continue

            pos_match = re.findall(pos_re, pos)
            if len(pos_match)==0:
                # TODO: log error to a log file
                continue

            # create a dictionary representation of the clipping
            clipping_dict = dict()
            clipping_dict["ctype"] = ctype
            clipping_dict["body"] = body
            clipping_dict["start"] = int(pos_match[0][0])
            if ctype == "highlight":
                clipping_dict["end"] = int(pos_match[0][1])

            # add the clipping to the corresponding book
            if title in books:
                if ctype in books[title]:
                    books[title][ctype].append(clipping_dict)
            else:
                # create a new entry in the books dict
                books[title] = dict()
                books[title]["author"] = author
                books[title]["subtitle"] = subtitle
                books[title]["highlight"] = []
                books[title]["note"] = []
                books[title][ctype].append(clipping_dict)

        return books

# separate short highlights without a note and add them to a single file
def add_anki_words(title, highlights):
    book_highlights = []
    with open(f"{OUT_DIR}/{ANKI_FILE}", mode="a") as af:
        print("\n#", title, file=af)
        for h in highlights:
            # highlights with less than LEN words and without a note are for Anki
            if (len(h["body"].split()) <= LEN) and "note" not in h:
                clean = h["body"].strip(".,:; (){}!?-'\"‘’“”«»").replace("’","'")
                print(clean, file=af)
            else:
                book_highlights.append(h)

    return book_highlights

# connect notes to the corresponding highlights and sort by position
def connect_notes_to_highlight(notes, highlights):
    # sort on the starting position
    notes = sorted(notes, key=lambda d: d["start"])
    highlights = sorted(highlights, key=lambda d: d["start"])

    s = 0
    for note in notes:
        for i in range(s, len(highlights)):
            h = highlights[i]
            # the note can be anywhere within its highlight
            if (note["start"] >= h["start"] and note["start"] <= h["end"]):
                # store the note inside the corresponding highlight
                highlights[i]["note"] = note["body"]
                s = i
                break
        else:
            print("Error: no matching highlight found for note")
            print(note)

    return highlights


def main():
    # check that the output directory is present
    if not os.path.isdir(OUT_DIR):
        if os.path.isfile(OUT_DIR):
            os.remove(OUT_DIR)
        os.mkdir(OUT_DIR)
    # delete temporary Anki file if already existing (left from previous run)
    if os.path.isfile(f"{OUT_DIR}/{ANKI_FILE}"):
        os.remove(f"{OUT_DIR}/{ANKI_FILE}")

    # parse My Clippings.txt
    books = parse_my_clippings()

    # convert clippings to Anki words and book notes
    for title, d in books.items():
        print(f"\n{title}")
        highlights = d["highlight"]

        # match highlight to corresponding note
        highlights = connect_notes_to_highlight(d["note"], d["highlight"])

        n_tot_highlights = len(highlights)

        # separate words for Anki
        highlights = add_anki_words(title, highlights)

        n_book_highlights = len(highlights)
        n_anki_highlights = n_tot_highlights - n_book_highlights
        print(f"Added {n_anki_highlights} Anki words and {n_book_highlights} highlights")

        # format book highlights for Obsidian


if __name__ == "__main__":
    main()
