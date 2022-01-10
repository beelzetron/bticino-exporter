# bticino Cloud Prometheus exporter
This repository contains a Prometheus custom exporter to scrape data from bticino/legrand cloud.

## Usage
To use the exporter you'll need to create an app on https://auth.netatmo.com and use provided client_id and client_secret along with your username and password.

```
podman run -d -p 9999:9999 -e API_CLIENT_ID=<bticino-app-id> -e API_CLIENT_SECRET=<bticino-app-secret> -e API_USERNAME="<bticino-user-username>" -e API_PASSWORD="<bticino-user-password>"
```