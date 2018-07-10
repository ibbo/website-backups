#/bin/bash

latestweb=$(gsutil ls -l gs://rscds-youth-website-backups | sort -k2 | tail -3 | sed -n '2p' | awk '{ print $3 }')

gsutil cp $latestweb .
