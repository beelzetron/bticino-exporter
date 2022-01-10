import authlib.oauth2.rfc8628
from authlib.integrations.requests_client import OAuth2Session
import time
import os
from prometheus_client import start_http_server, Gauge

base_url = 'https://api.netatmo.com'


class CollectMetrics:
    def __init__(self, polling_interval_seconds=30):
        self.polling_interval_seconds = polling_interval_seconds

        self.base_url = base_url
        self.token_url = self.base_url + '/oauth2/token'
        # Scopes required to read the bticino smart data
        self.scopes = ['read_magellan', 'read_station']
        # Credentials are read from environment variables
        self.client_id = os.environ.get('API_CLIENT_ID')
        self.client_secret = os.environ.get('API_CLIENT_SECRET')
        self.username = os.environ.get('API_USERNAME')
        self.password = os.environ.get('API_PASSWORD')

        # Error out if one of the required variables is missing
        if self.client_id == "" or self.client_secret == "" or self.username == "" or self.password == "":
            print("FATAL: No credentials configured")
            exit(1)

        # OAuth2 authentication
        self.client = OAuth2Session(client_id=self.client_id,
                                    client_secret=self.client_secret,
                                    scope=self.scopes
                                    )
        self.token = self.client.fetch_token(self.token_url,
                                             username=self.username,
                                             password=self.password
                                             )

        # Metrics definition
        self.power_usage = Gauge("current_power_usage_watts",
                                 "Current power usage in watt",
                                 ["name", "id"]
                                 )
        self.firmware_revision = Gauge("current_firmware_revision",
                                       "Current firmware revision",
                                       ["name", "id"]
                                       )

    def _get_api(self, url, params=None, headers=None):
        try:
            resp = self.client.get(url=url, params=params, headers=headers)
            return resp
        except authlib.oauth2.rfc8628.ExpiredTokenError:
            self.client.refresh_token(self.token_url, refresh_token=self.token)
            resp = self.client.get(url=url, params=params)
            return resp

    def get_homes(self):
        return self._get_api(url=self.base_url + '/api/homesdata').json()

    def get_home_status(self, home_id):
        query = {'home_id': home_id}
        resp = self._get_api(url=self.base_url + '/api/homestatus', params=query).json()
        print(resp)
        return resp

    def _clean_id(self, id):
        return id.replace(':', '')

    def run_loop(self):
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        home_status = {}
        homes = self.get_homes()['body']
        for home in homes['homes']:
            devices = {}
            for dev in home['modules']:
                id = self._clean_id(dev['id'])
                devices[id] = {}
                device_info = {
                    'name': dev['name'],
                    'type': dev['type']
                }
                devices[id] = device_info
            home_status[home['id']] = self.get_home_status(home['id'])['body']['home']['modules']
        for stat in home_status:
            for dev_status in home_status[stat]:
                dev_id = self._clean_id(dev_status['id'])
                devices[dev_id]['firmware_revision'] = dev_status['firmware_revision']
                self.firmware_revision.labels(name=devices[dev_id]['name'],
                                              id=dev_status['id']).set(devices[dev_id]['firmware_revision'])
                if 'NLP' in dev_status['type']:
                    devices[dev_id]['power'] = dev_status['power']
                    self.power_usage.labels(name=devices[dev_id]['name'],
                                            id=dev_status['id']).set(dev_status['power'])


if __name__ == "__main__":
    collector = CollectMetrics()
    start_http_server(9999)
    collector.run_loop()
