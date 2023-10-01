# Kindle highlights script

A script to extract and parse Kindle highlights and notes from `My Clippings.txt`.

![kindle_highlights](https://github.com/GBergatto/kindle-highlights/assets/69045457/e61e8ac6-b967-40b3-bc32-856f45860876)

When I read, I _highlight important passages and take short notes_ on some of them. When I'm done with the book, I want to move these highlights into my [Obisidian](https://obsidian.md/) vault to expand on them.
In addition, I also highlight _single words and short sentences_ that I want to learn to _expand my vocabulary_. To memorize them, I then use the space-repetition software [Anki](https://apps.ankiweb.net/).

This script facilitates my workflow by formatting highlights and notes into one markdown file for each book and by adding all new words into a single file that I keep on my computer so that I can later turn them into Anki flashcards.

## How it works

After having connected the Kindle device to your computer via USB cable, run the Bash script `kindle_highlight.sh`.

This script will
1. Mount the Kindle device, assuming it's located at `sda/sda1`
2. Copy `My Clippings.txt` from it to the directory where the script is located
3. Run the Python parser
4. Copy the book notes to the Obsidian vault and append the new words to the designated file
5. Copy the updated `My Clippings.txt` file back to the Kindle
6. Unmount the Kindle device

The Python parser will
1. Extract clippings from the clipping file and sort them by book
2. Ask the user which books haven't been completed yet and store their clippings in the new clippings file to put back in the Kindle
3. Connect each note to the corresponding highlight
4. Separate short highlights without a note to add them to the list of new words to learn
5. For each book, put all other highlights and notes (book notes) into a markdown file which will be copied into the Obsidian vault
