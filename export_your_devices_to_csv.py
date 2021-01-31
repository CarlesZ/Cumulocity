import sys
import csv
import requests
from requests.auth import HTTPBasicAuth
#change the datefrom and datato > year-month-day
query = 'dateFrom=2020-01-01&dateTo=2020-12-31'
output = 'export.csv'

tenant = sys.argv[1]
auth = HTTPBasicAuth(sys.argv[2], sys.argv[3])
cache = {}


def get_device(source):
    if source not in cache:
        response = requests.get('https://' + tenant + '/inventory/managedObjects/' + source, auth=auth)
        name = response.json()['name']
        cache[source] = name
    return cache[source]


def export_measurement(writer, msrmt):
    time = msrmt['time']
    source = msrmt['source']['id']
    name = get_device(source)

    for fragment_name, fragment in msrmt.iteritems():
        if fragment_name != 'source' and type(fragment) is dict:
            for series_name, series in fragment.iteritems():
                data_point = fragment_name + ' ' + series_name
                value = series['value']
                unit = series['unit'] if 'unit' in series else ''
                writer.writerow([time, source, name, data_point, value, unit])


def get_page(url):
    response = requests.get(url, auth=auth)
    mp = response.json()['measurements']
    np = response.json()['next']
    return mp, np


with open(output, 'wb') as csvfile:
    w = csv.writer(csvfile)
    w.writerow(['Time', 'Device ID', 'Device name', 'Data point', 'Value', 'Unit'])

    sys.stdout.write('Starting export')
    sys.stdout.flush()
    measurements, next_page = get_page('https://' + tenant + '/measurement/measurements?pageSize=2000&' + query)

    while len(measurements) > 0:
        sys.stdout.write('.')
        sys.stdout.flush()
        for measurement in measurements:
            export_measurement(w, measurement)
        measurements, next_page = get_page(next_page)
