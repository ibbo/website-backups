#!/usr/bin/env python

import sys

from google.cloud import storage
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pprint import pprint, pformat

import json
import requests

import itertools as it

def get_blobs():
    client = storage.Client()

    bucket_name = 'rscds-youth-website-backups'

    bucket = client.get_bucket(bucket_name)

    blobs = [i for i in bucket.list_blobs()]
    return blobs

def get_old_blobs(blobs):
    # Need an offset-aware datetime to do the comparison below, so
    # create one by using the timezone from one of the blobs
    d = datetime.now(blobs[0].time_created.tzinfo)

    threshold = d - relativedelta(years=1)

    old_blobs = [i for i in blobs if i.time_created < threshold]
    return old_blobs

# get_all_old_blobs_except_last_in_month - This function encodes
#   the backup rules we want to enforce. We keep all backups in
#   the current month. For all months prior to this we only keep
#   the last backup in the month.
def get_all_old_blobs_except_last_in_month(blobs):
    d = datetime.now(blobs[0].time_created.tzinfo)

    # Don't include the current month
    threshold = d - relativedelta(months=1)

    blobs_old = []
    # Group all the blobs by month and append all but the last of
    # them to the list of old blobs.
    for k, g in it.groupby(blobs, lambda x: x.time_created.month):
        allblobs = list(g)
        if len(allblobs) > 1:
            # Check that we're not in the current month before
            # appending, because we want to keep all the blobs
            # in the current month.
            if allblobs[0].time_created < threshold:
                blobs_old.extend(allblobs[:-1])

    return blobs_old

def get_large_blobs(blobs):
    large_blobs = [i for i in blobs if i.size > 100000000]
    return large_blobs

def display_blobs():
    blobs = get_blobs()
    print("All blobs:")
    pprint(blobs)

    old_blobs = get_old_blobs(blobs)

    print("Blobs older than 1 year: ")
    pprint(old_blobs)

    large_blobs = get_large_blobs(blobs)

    print("Blobs over 100MB: ")
    pprint(large_blobs)

    monthly_old_blobs = get_all_old_blobs_except_last_in_month(blobs)
    print("Blobs over 1 month, except last in month: ")
    pprint(monthly_old_blobs)

def delete_old_blobs(mailgunkey = None):
    blobs = get_blobs()
    old_blobs = get_old_blobs(blobs)
    print('Deleting %d old backup files' % (len(old_blobs)))
    if len(old_blobs) > 0:
        delete_blobs(old_blobs)
        email_backup_message("Website backups deleted backups older than a year", pformat(old_blobs), mailgunkey)

def delete_large_blobs(mailgunkey = None):
    blobs = get_blobs()
    large_blobs = get_large_blobs(blobs)
    print('Deleting %d large blobs' % (len(large_blobs)))
    delete_blobs(large_blobs)

def delete_old_monthly_blobs(mailgunkey = None):
    blobs = get_blobs()
    monthly_blobs = get_all_old_blobs_except_last_in_month(blobs)
    print('Deleting %d old monthly backup files' % (len(monthly_blobs)))
    if len(monthly_blobs) > 0:
        delete_blobs(monthly_blobs)
        email_backup_message("Website backups deleted old monthly backups", pformat(monthly_blobs), mailgunkey)

def delete_blobs(blobs):
    for i in blobs:
        print('Deleting blob: %s' %(i))
        i.delete()

def load_creds(credsfile):
    with open(credsfile) as f:
        data = json.load(f)
    return data

def test_email(mailgunkey = None):
    if mailgunkey:
        return requests.post(
            "https://api.mailgun.net/v3/mail.rscds-youth.org/messages",
            auth=("api", mailgunkey),
            data={"from": "Website Backups <website@rscds-youth.org>",
                  "to": ["thomas.ibbotson@gmail.com"],
                  "subject": "Website backups test email",
                  "text": "This is a test"})

def email_backup_message(subject="", text="", mailgunkey = None):
    if mailgunkey:
        return requests.post(
            "https://api.mailgun.net/v3/mail.rscds-youth.org/messages",
            auth=("api", mailgunkey),
            data={"from": "Website Backups <website@rscds-youth.org>",
                  "to": ["info@rscds-youth.org"],
                  "subject": subject,
                  "text": text})

if __name__ == '__main__':
    creds = load_creds('credentials/app_creds.json')
    if sys.argv[1] == 'display':
        display_blobs()   
    elif sys.argv[1] == 'delete-old':
        delete_old_blobs(creds['mailgunkey'])
    elif sys.argv[1] == 'delete-large':
        delete_large_blobs(creds['mailgunkey'])
    elif sys.argv[1] == 'delete-monthly':
        delete_old_monthly_blobs(creds['mailgunkey'])
    elif sys.argv[1] == 'test-email':
        test_email(creds['mailgunkey'])

