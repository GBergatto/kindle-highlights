#! /usr/bin/python

import os
import re
import sys

SEPARATOR = "==========\n"
LEN = int(sys.argv[1])
OUT_DIR = sys.argv[2]
ANKI_FILE = sys.argv[3]
CLIPPINGS_FILE = sys.argv[4]

title_re = re.compile("^(.*)\((.*)\)$")
meta_re = re.compile("^-\s*Your (\S+) (.*)Added on\s+(.+)$")
pos_re = re.compile("Location (\d+)(?:-(\d+)|)")


def parse_my_clippings():
    books = dict()

    with open(CLIPPINGS_FILE, mode="r", encoding="utf-8-sig") as cf:
        clippings = cf.read().split(SEPARATOR)[:-1]
        book_clippings = dict()

        for c in clippings:
            split_c = c.split("\n")
            title_line = split_c[0]
            meta_line = split_c[1]
            # the 3rd and last elements of the list are empty strings
            body = "\n".join(split_c[3:-1])

            # parse title, subtitle and author
            title_match = re.match(title_re, title_line) 
            if not title_match:
                print(f"Error: cannot parse title. Skipping.\n'{title_line}'\n")
                continue

            full_title, author = title_match.groups()
            full_title = full_title.strip().strip("\ufeff")
            ft_split = full_title.split(":")
            title = ft_split[0]
            subtitle = ""
            if (len(ft_split)>1):
                subtitle = ft_split[1].strip()

            # keep the clipping string for unfinished books
            if title in book_clippings:
                book_clippings[title].append(c)
            else:
                book_clippings[title] = [c]

            # parse type, position and date
            meta_match = re.match(meta_re, meta_line)
            if not meta_match:
                print(f"Error: cannot parse metadata. Skipping.\n'{meta_line}'\n")
                continue

            # date is not used
            ctype, pos, _ = meta_match.groups()
            ctype = ctype.lower()

            if ctype == "bookmark":
                continue

            pos_match = re.findall(pos_re, pos)
            if len(pos_match)==0:
                print(f"Error: cannot parse position. Skipping.\n'{pos}'\n")
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

        titles = list(reversed(books.keys()))
        print(f"Books found in {CLIPPINGS_FILE}")
        for i, t in enumerate(titles):
            print(f"{i}. {t}")
        print("Which one of them, if any, haven't you completed yet?")

        # get the indexes of all uncompleted books
        to_skip = []
        valid = False
        while not valid:
            answer = input("Enter as a space-separated list of numbers: ").strip()

            try:
                indexes = [int(x) for x in answer.split()]
                valid = True
                for i in indexes:
                    if (i < 0 or i >= len(books)):
                        print(i, "is not a valid index.")
                        valid = False

                if not valid:
                    print(f"All indexes must be between 0 and {len(books)-1}")
                else:
                    to_skip = [titles[x] for x in indexes]

            except ValueError:
                print("Invalid format.")

        print()
        # do not parse clippings for uncompleted books
        for t in titles:
            if t in to_skip:
                print(f"Skipped '{t}'")
                del books[t]

        # keep clippings of uncompleted books inside clipping file
        with open(f"{OUT_DIR}/{CLIPPINGS_FILE}", mode="w") as ncf:
            content = ""
            for title, clipping in book_clippings.items():
                if title in to_skip:
                    content += SEPARATOR.join(clipping)
            if content:
                # don't add separator to an empty file
                content += SEPARATOR
            ncf.write(content)

        return books


# separate short highlights without a note and add them to a single file
def add_anki_words(title, highlights):
    book_highlights = []
    with open(f"{OUT_DIR}/{ANKI_FILE}", mode="a") as af:
        print("\n#", title, file=af)
        for h in highlights:
            # highlights with less than LEN words and without a note are for Anki
            if (len(h["body"].split()) <= LEN) and "note" not in h:
                clean = h["body"].strip(".,:; (){}!?—-'\"‘’“”«»").replace("’","'")
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


# create a markdown file and print book highlights to it
def create_book_note(title, highlights):
    f_title = title.replace(" ", "_")
    f_title =  "".join(x for x in f_title if (x.isalnum() or x == "_"))

    with open(f"{OUT_DIR}/{f_title}.md", mode="w") as file:
        for h in highlights:
            body = h["body"][0].upper() + h["body"][1:].strip(" —-:,")
            body = re.sub("[“”«»]", "\"", body)
            body = re.sub("[‘’]", "'", body)
            formatted = f"> {body}\n"
            if "note" in h:
                note = h["note"][0].upper() + h["note"][1:]
                formatted += f"\n{note}\n"
            print(formatted, file=file)


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
        create_book_note(title, highlights)


if __name__ == "__main__":
    main()
