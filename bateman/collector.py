import os
import sys
import logging
from datetime import datetime as dt
import spivey
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


def main():
    # TODO: make a config file
    load_dotenv()
    try:
        token = os.environ['INFLUXDB_TOKEN']
    except KeyError as e:
        logging.critical('%s environment variable not found',  e)
        sys.exit(1)

    org = 'default'
    bucket = 'main'
    influx_url = 'http://192.168.1.10:8086'

    with InfluxDBClient(url=f'{influx_url}', token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        #TODO
        # - figure out batch settings
        # - test putting theta and delta under greeks
        # - unfuck this mess - try building a dict and passing it to Point
        # - figure out how to use ms precision (may need to set timezone when using time)
        #   .time(dt.now(), write_precision=WritePrecision.MS)
        # - get a config file working
        # - abstract this out so it can collect the underlying for $VIX.X too
        # - make a ui/api to CRUD jobs

        s = spivey.Client()
        o = s.options('$VIX.X', 90)
        points = []

        for _action in ['putExpDateMap', 'callExpDateMap']:
            for i in o[_action].keys():
                for j in o[_action][i].keys():
                    for k in o[_action][i][j]:
                        p = Point('options') \
                            .tag('exp', dt.fromtimestamp(k['expirationDate']/1000).strftime('%d %b %y').upper()) \
                            .tag('strike', k['strikePrice']) \
                            .tag('symbol', '$VIX.X') \
                            .tag('putCall', k['putCall'].lower()) \
                            .field('bid', k['bid']) \
                            .field('ask', k['ask']) \
                            .field('openInterest', k['openInterest']) \
                            .field('volume', k['totalVolume']) \
                            .field('theta', float(k['theta'])) \
                            .field('delta', float(k['delta'])) \
                            .field('volatility', float(k['volatility'])) \
                            .field('daysToExpiration', k['daysToExpiration']) \
                            .field('percentChange', k['percentChange']) \
                            .field('mark', k['mark']) \
                            .field('timeValue', k['timeValue'])
                        points.append(p)
        logging.info(f'Storing {len(points)} contracts')
        write_api.write(bucket, org, points)

if __name__ == '__main__':
    logging.info('Started %s', __file__.rsplit('/', maxsplit=1)[-1])
    sched = BlockingScheduler()
    sched.add_job(main, trigger='cron', day_of_week='1-5', hour='14-21', second='*/30')
    sched.start()
