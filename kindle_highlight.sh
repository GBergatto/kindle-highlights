#! /bin/bash

# get directory of the script
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )

KINDLE_DIR=/run/media/gb/Kindle
OBSIDIAN_ROOT=/home/gb/Dropbox/Obsidian/Cervello
WORDS_FILE=/home/gb/Documents/wordsFromKindle.txt
OUT_DIR=out
ANKI_FILE=anki.txt
CLIPPINGS_FILE=My_Clippings.txt

# mount Kindle
if udisksctl mount -b /dev/sda1; then
  echo

  if [ -f $KINDLE_DIR/documents/My\ Clippings.txt ];
  then
    # move My Clipping.txt to DIR
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

