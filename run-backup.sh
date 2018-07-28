#!/bin/bash

export GOOGLE_APPLICATION_CREDENTIALS=/home/rscds/website-backups/credentials/google_app_creds.json

cd /home/rscds/website-backups
php /home/rscds/website-backups/backup.php $*

# Now delete old monthly backups
python /home/rscds/website-backups/delete_backups.py delete-monthly

# And backups older than a year
python /home/rsdcs/website-backups/delete_backups.py delete-old
