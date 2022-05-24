import os
import sys
import argparse
import logging
from datetime import datetime as dt
import spivey
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(format='%(levelname)s %(message)s',
                    level=logging.INFO)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Collect stock market data')
    parser.add_argument('ticker', nargs=1, type=str)
    parser.add_argument('-d', '--days', type=int, default=90)
    parser.add_argument('-t', '--type', dest='security_type', help='security type',
                        choices=['stock', 'option'], default='option')

    return parser.parse_args()

def stock(ticker, client):
    last = client.underlying(ticker)
    try:
        return Point('underlying').tag('symbol', ticker).field('last', float(last))
    except TypeError:
        return Point('underlying').tag('symbol', ticker).field('last', None)

def options(ticker, client, days):
    o = client.options(ticker, days)
    points = []

    for _action in ['putExpDateMap', 'callExpDateMap']:
        for i in o[_action].keys():
            for j in o[_action][i].keys():
                for k in o[_action][i][j]:
                    points.append(Point('options') \
                        .tag('exp', dt.fromtimestamp(k['expirationDate']/1000).strftime('%d %b %y').upper()) \
                        .tag('strike', k['strikePrice']) \
                        .tag('symbol', ticker) \
                        .tag('putCall', k['putCall'].lower()) \
                        .field('bid', k['bid']) \
                        .field('ask', k['ask']) \
                        .field('openInterest', k['openInterest']) \
                        .field('volume', k['totalVolume']) \
                        .field('theta', float(k['theta'])) \
                        .field('delta', float(k['delta'])) \
                        .field('volatility', float(k['volatility'])) \
                        .field('mark', k['mark'])
                    )
    return points

def main(ticker, security_type, client, days):
    # TODO: make a config file
    load_dotenv()
    try:
        token = os.environ['INFLUXDB_TOKEN']
    except KeyError as e:
        logging.critical('%s environment variable not found', e)
        sys.exit(1)

    org = 'default'
    bucket = 'main'
    influx_url = 'http://192.168.1.10:8086'

    with InfluxDBClient(url=f'{influx_url}', token=token, org=org) as influx_client:
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)
        #TODO
        # - figure out batch settings
        # - test putting theta and delta under greeks
        # - unfuck this mess - try building a dict and passing it to Point
        # - figure out how to use ms precision (may need to set timezone when using time)
        #   .time(dt.now(), write_precision=WritePrecision.MS)
        # - get a config file working
        # - make a ui/api to CRUD jobs
        # - force utc
        if security_type == 'stock':
            points = stock(ticker, client)
        else:
            points = options(ticker, client, days)

        logging.info('Storing %s data', ticker)
        write_api.write(bucket, org, points)

if __name__ == '__main__':
    logging.info('Started %s', __file__.rsplit('/', maxsplit=1)[-1])
    args = parse_arguments()
    c = spivey.Client()
    sched = BlockingScheduler()
    sched.add_job(
        main, args=(args.ticker[0].upper(), args.security_type, c, args.days),
        trigger='cron', day_of_week='0-4', hour='13-19', second='*/30'
    )
    sched.start()
