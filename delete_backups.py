#!/usr/bin/env python

import sys

from google.cloud import storage
from dateutil.relativedelta import relativedelta
from datetime import datetime
from pprint import pprint


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

def delete_old_blobs():
    blobs = get_blobs()
    old_blobs = get_old_blobs(blobs)
    print('Deleting %d old backup files' % (len(old_blobs)))
    for i in old_blobs:
        print('Deleting: %s' %(i))
        i.delete()

def delete_large_blobs():
    blobs = get_blobs()
    large_blobs = get_large_blobs(blobs)
    print('Deleting %d large blobs' % (len(large_blobs)))
    for i in large_blobs:
        print('Deleting large blob: %s' %(i))
        i.delete()

if __name__ == '__main__':
    if sys.argv[1] == 'display':
        display_blobs()   
    elif sys.argv[1] == 'delete-old':
        delete_old_blobs()
    elif sys.argv[1] == 'delete-large':
        delete_large_blobs()
