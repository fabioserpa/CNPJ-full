#!/bin/bash
aria2c -d /tmp/persist_to_workspace/data -s 16 -x 16 | xargs -d \n -a $1
