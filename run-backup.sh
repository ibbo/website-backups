#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS=/home/rscds/website-backups/credentials/google_app_creds.json

cd /home/rscds/website-backups
php /home/rscds/website-backups/backup.php $*
