#!/usr/bin/python3
import click
import csv
import requests
import json
from urllib.parse import urljoin

BATCH_SIZE = 10000

@click.command()
@click.argument('likefile', type=click.Path())
@click.option('--url', default="http://127.0.0.1:5000/", type=click.STRING)
@click.option('--delete-all-data', default=False, is_flag=True)
def ingest(likefile, url, delete_all_data):

    def _url(endpoint):
        return urljoin(url, endpoint)

    if delete_all_data:
        requests.request('DELETE', _url('v1/maintenance/delete-all-data'))

    user_item_tuples = list()
    with open(likefile, encoding='latin1') as f:
        r = csv.reader(f, delimiter=';', skipinitialspace=True, quoting=csv.QUOTE_ALL)
        next(r) # header row
        for row in r:
            if row[2] != '0' and row[2] < '5':
                continue
            user_item_tuples.append((row[0], row[1]))

    for i in range(0, len(user_item_tuples), BATCH_SIZE):
        data = {'likes': user_item_tuples[i: i+BATCH_SIZE]}
        requests.request('POST',
            _url('/v1/likes/bulk'),
            data=json.dumps(data),
            headers={'content-type':'application/json'})

if __name__ == '__main__':
    ingest()
