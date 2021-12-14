import os
import sys
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

# TODO: make a config file
load_dotenv()
try:
    token = os.environ['INFLUXDB_TOKEN']
except KeyError as e:
    print(f'{e} environment variable not found')
    sys.exit(1)

org = 'personal'
bucket = 'why'
influx_url = 'http://192.168.1.10'
influx_port = '8086'

with InfluxDBClient(url=f'{influx_url}:{influx_port}', token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for i in range(1, 20):
#        data = f"mem,host=host2 used_percent={i}"
        #p = Point("my_measurement").tag("location", "New Mexico").field("temperature", i)
        p = Point("$VIX.X").tag("exp", "19 JAN 22").field("strike", i)

        write_api.write(bucket, org, p)
        time.sleep(1)
