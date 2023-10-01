#! /bin/bash

# get directory of the script
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

# directory inside $SCRIPT_DIR for output of the parser
OUT_DIR=out
# temporary file where the parser adds new words
ANKI_FILE=anki.txt
# clippings file inside $SCRIPT_DIR (renamed to avoid issues with the space)
CLIPPINGS_FILE=My_Clippings.txt

### Edit to adapt the script to your filesystem

# directory in your Obsidian Vault where you want book notes to be copied to
OBSIDIAN_ROOT=/home/gb/Dropbox/Obsidian/Cervello
# file that contains all new words sorted by book
WORDS_FILE=/home/gb/Documents/wordsFromKindle.txt

###

# mount Kindle
KINDLE_DIR=$(udisksctl mount -b /dev/sda1 | cut -d' ' -f4)
if [[ -n $KINDLE_DIR ]]; then
  echo "Mounted Kindle at $KINDLE_DIR"
  echo

  if [ -f $KINDLE_DIR/documents/My\ Clippings.txt ];
  then
    # move My Clipping.txt to SCRIPT_DIR
    cp $KINDLE_DIR/documents/My\ Clippings.txt $SCRIPT_DIR/$CLIPPINGS_FILE

    # run Python parser
    $SCRIPT_DIR/clippings_parser.py 3 $OUT_DIR $ANKI_FILE $CLIPPINGS_FILE
    rm $SCRIPT_DIR/$CLIPPINGS_FILE
    echo

    # ask for confirmation to proceed
    read -p "Do you want to proceed? [Y/n] "
    echo
    if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]];
    then
      # append ANKI_FILE to WORDS_FILE
      echo "Appending $SCRIPT_DIR/$OUT_DIR/$ANKI_FILE to $WORDS_FILE"
      cat $SCRIPT_DIR/$OUT_DIR/$ANKI_FILE >> $WORDS_FILE
      rm $SCRIPT_DIR/$OUT_DIR/$ANKI_FILE
      echo

      # move book notes to root of Obsidian vault
      echo "Copying book notes to $OBSIDIAN_ROOT"
      mv $SCRIPT_DIR/$OUT_DIR/*.md $OBSIDIAN_ROOT/
      echo

      echo "Copying clippings for uncompleted books back to Kindle"
      rm $KINDLE_DIR/documents/My\ Clippings.txt
      mv $SCRIPT_DIR/$OUT_DIR/$CLIPPINGS_FILE $KINDLE_DIR/documents/My\ Clippings.txt
      echo

      rmdir $SCRIPT_DIR/$OUT_DIR

    fi

  else
    echo "Error: 'My Clippings.txt' not found"
  fi

  udisksctl unmount -b /dev/sda1
else
  echo "Error: Kindle not found."
fi

