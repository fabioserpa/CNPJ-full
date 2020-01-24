#!/bin/bash
aria2c -d /tmp/cnpj_data -s 16 -x 16 | xargs -d \n -a $1
