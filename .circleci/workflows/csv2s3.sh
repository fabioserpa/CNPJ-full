#!/bin/bash
if [ -z "$1"  ]; then
  echo "Version arg not set"
  exit 1
fi

version=$1
tar zcvf csv.tar.gz ./csv
aws s3api put-object --body csv.tar.gz --bucket company-cnpj-prd --key $version/csv_$version.tar.gz
