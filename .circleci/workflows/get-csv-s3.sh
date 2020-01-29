#!/bin/bash
if [ -z "$1"  ]; then
  echo "Version arg not set"
  exit 1
fi

if [ -z "$2"  ]; then
  echo "lockfile arg not set"
  exit 1
fi

version=$1
lockfile=$2
aws s3api head-object --bucket company-cnpj-prd --key $version/csv_$version.tar.gz && exist=true
if [ $exist ]; then
  touch $lockfile
  aws s3api get-object --bucket company-cnpj-prd --key $version/csv_$version.tar.gz csv.tar.gz
  tar -zxvf csv.tar.gz
fi
exit 0
