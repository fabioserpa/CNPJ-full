#!/bin/bash
linkfile=$1
while read link; do
  aria2c -d ./data -s16 -x16 $link &
  echo "Downloading $link"
done < $linkfile
wait
