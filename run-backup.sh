#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS=/home/rscds/website-backups/credentials/google_app_creds.json

php /home/rscds/website-backups/backup.php $*
