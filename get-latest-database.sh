#/bin/bash

latestdb=$(gsutil ls -l gs://rscds-youth-website-backups | sort -k2 | tail -3 | sed -n '1p' | awk '{ print $3 }')

gsutil cp $latestdb .
