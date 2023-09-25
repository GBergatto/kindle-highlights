#! /usr/bin/python

import os
import re
import sys

LEN = int(sys.argv[1])
SEPARATOR = "==========\n"
OUT_DIR = "out"

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

            pos_match = re.findall(pos_re, pos)
            if len(pos_match)==0:
                # TODO: log error to a log file
                continue
            start = int(pos_match[0][0])
            end = None
            # Highlights are the only type of clipping with a start and an end position
            if ctype == "highlight":
                end = int(pos_match[0][1])

            # create a dictionary representation of the clipping
            clipping_dict = dict()
            clipping_dict["ctype"] = ctype
            clipping_dict["body"] = body
            clipping_dict["start"] = start
            if ctype == "highlight":
                clipping_dict["end"] = end

            # classify clippings into highlights, anki words, notes and bookmarks
            if ctype == "highlight":
                if (len(body.split()) <= LEN):
                    ctype = "anki"

            # add the clipping to the corresponding book
            if title in books:
                if ctype in books[title]:
                    books[title][ctype].append(clipping_dict)
                else:
                    # create a new list for this clipping type
                    books[title][ctype] = [clipping_dict]
            else:
                # create a new entry in the books dict
                books[title] = dict()
                books[title]["author"] = author
                books[title]["subtitle"] = subtitle
                books[title][ctype] = [clipping_dict]

        return books


# Create a single file in OUT_DIR with all Anki words separated by title
def add_anki_words(title, words):
    if not os.path.isdir(OUT_DIR):
        if os.path.isfile(OUT_DIR):
            os.remove(OUT_DIR)
        os.mkdir(OUT_DIR)

    with open(f"{OUT_DIR}/anki.txt", mode="a") as af:
        print("\n#", title, file=af)
        for w in words:
            clean = w["body"].strip(".,:; (){}!?-'\"‘’“”«»").replace("’","'")
            print(clean, file=af)


def main():
    books = parse_my_clippings()
    for title, d in books.items():
        # append Anki words to file
        print(title)
        if "anki" in d:
            add_anki_words(title, d["anki"])

        # match highlight to corresponding note

        # create book note


if __name__ == "__main__":
    main()
