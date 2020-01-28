#!/bin/bash
aws s3api head-object --bucket company-cnpj-prd --key $1/csv_$1.tar.gz && exist=true
if [ $exist ]; then
  touch s3.lock
  aws s3api get-object --bucket company-cnpj-prd --key $1/csv_$1.tar.gz csv.tar.gz
  tar zxvf csv.tar.gz
fi
exit 0
