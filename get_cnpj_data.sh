#!/bin/bash
xargs -a $1 aria2c -d /tmp/persist_to_workspace/data -s 16 -x 16
