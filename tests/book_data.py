#!/usr/bin/python3
import click
import csv
import requests
import json
import random
import time
import re
from urllib.parse import urljoin


BATCH_SIZE = 10000
no_id = re.compile(r'[^a-zA-Z0-9\-_]')
def idlize(string):
    return no_id.sub('', string)

def load(likefile):
    user_item_tuples = []
    with open(likefile, encoding='latin1') as f:
        r = csv.reader(f, delimiter=';', skipinitialspace=True, quoting=csv.QUOTE_ALL)
        next(r)  # header row
        for row in r:
            if row[2] != '0' and row[2] < '5':
                continue
            user_item_tuples.append((idlize(row[0]), idlize(row[1])))
    return user_item_tuples


@click.group()
def grp():
    pass

@grp.command()
@click.argument('likefile', type=click.Path())
@click.option('--url', default="http://127.0.0.1:5000/", type=click.STRING)
@click.option('--delete-all-data', default=False, is_flag=True)
def ingest(likefile, url, delete_all_data):

    def _url(endpoint):
        return urljoin(url, endpoint)

    if delete_all_data:
        requests.request('DELETE', _url('v1/maintenance/delete-all-data'))

    user_item_tuples = load(likefile)

    for i in range(0, len(user_item_tuples), BATCH_SIZE):
        data = {'likes': user_item_tuples[i: i + BATCH_SIZE]}
        res = requests.request('POST',
            _url('/v1/likes/bulk'),
            data=json.dumps(data),
            headers={'content-type': 'application/json'})
        if res.status_code != 200:
            print(res.content)


@grp.command()
@click.argument('likefile', type=click.Path())
@click.argument('count', type=click.INT)
@click.option('--url', default="http://127.0.0.1:5000/", type=click.STRING)
def recommend(likefile, count, url):

    def _url(endpoint):
        return urljoin(url, endpoint)

    user_item_tuples = load(likefile)

    start = time.time()
    for user_id, item_id in random.sample(user_item_tuples, count):
        res = requests.request('GET',
            _url('/v1/recommendations/user/{}?count={}'.format(user_id, 6)))
        print(res.json())
    print('querying took %4.2f seconds' % (time.time() - start))


@grp.command()
@click.option('--url', default="http://127.0.0.1:5000/", type=click.STRING)
@click.option('--delete-all-data', default=False, is_flag=True)
def maintenance(likefile, url, delete_all_data):

    def _url(endpoint):
        return urljoin(url, endpoint)

    if delete_all_data:
        requests.request('DELETE', _url('v1/maintenance/delete-all-data'))


if __name__ == '__main__':
    grp()
