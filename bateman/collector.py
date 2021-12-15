import os
import sys
import time
from datetime import datetime as dt
from pytz import timezone
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
import spivey

# TODO: make a config file
load_dotenv()
try:
    token = os.environ['INFLUXDB_TOKEN']
except KeyError as e:
    print(f'{e} environment variable not found')
    sys.exit(1)

s = spivey.Client()
o = s.options('$VIX.X', 90)

org = 'default'
bucket = 'main'
influx_url = 'http://192.168.1.10'
influx_port = '8086'

with InfluxDBClient(url=f'{influx_url}:{influx_port}', token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    #TODO
    # - figure out batch settings
    # - make exp the right format, I think it's in the original bateman
    # - test putting theta and delta under greeks
    # - unfuck this mess
    # - figure out how to use ms precision (need to set timezone when using time)
    #   .time(dt.now(), write_precision=WritePrecision.MS)
    # - get a config file working
    # - make some dashboards

    points = []

    for _action in ['putExpDateMap', 'callExpDateMap']:
        for i in o[_action].keys():
            for j in o[_action][i].keys():
                for k in o[_action][i][j]:
                    p = Point('options') \
                        .tag('exp', dt.fromtimestamp(k['expirationDate']/1000,
                            tz=timezone('EST')).strftime('%d %b %y').upper()) \
                        .tag('strike', k['strikePrice']) \
                        .tag('symbol', '$VIX.X') \
                        .tag('putCall', k['putCall'].lower()) \
                        .field('bid', k['bid']) \
                        .field('ask', k['ask']) \
                        .field('openInterest', k['openInterest']) \
                        .field('volume', k['totalVolume']) \
                        .field('theta', k['theta']) \
                        .field('delta', k['delta']) \
                        .field('volatility', k['volatility']) \
                        .field('daysToExpiration', k['daysToExpiration']) \
                        .field('percentChange', k['percentChange']) \
                        .field('mark', k['mark']) \
                        .field('timeValue', k['timeValue'])
                    points.append(p)
    print(f'Sending {len(points)} contracts')
    write_api.write(bucket, org, points)
