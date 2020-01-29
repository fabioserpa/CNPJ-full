#!/bin/bash
tar zcvf csv.tar.gz ./csv
aws s3api put-object --body csv.tar.gz --bucket company-cnpj-prd --key $1/csv_$1.tar.gz
