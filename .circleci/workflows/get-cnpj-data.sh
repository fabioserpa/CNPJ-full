#!/bin/bash
if [ -z "$1"  ]; then
  echo "linkfile arg not set"
  exit 1
fi

linkfile=$1
while read link; do
  aria2c -d ./data -s16 -x16 $link &
  echo "Downloading $link"
done < $linkfile
wait
