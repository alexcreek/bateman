#!/usr/bin/env python3
from requests import post
import os
import sys

try:
    refresh_token = os.environ['REFRESH_TOKEN']
    client_id = os.environ['CLIENT_ID']
except KeyError as e:
    print(f'{e} environment variable not found')
    sys.exit(1)

payload = {
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token,
    'client_id':  client_id
}

auth_url = os.getenv('TD_AUTH_URL', 'https://api.tdameritrade.com/v1/oauth2/token')
timeout = int(os.getenv('TD_TIMEOUT', '30'))

resp = post(auth_url, data=payload, timeout=timeout)
print(resp.json())
