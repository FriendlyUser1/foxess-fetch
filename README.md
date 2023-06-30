# foxess-fetch
Simple FoxESS data fetching with python

## Setup
- Download [here](https://github.com/FriendlyUser1/foxess-fetch/archive/refs/heads/main.zip)
- Rename `example.config.json` to `config.json`.

In `config.json`:
- Insert your FoxESSCloud username and password.
- Insert your device's id (from the id parameter in the URL of inverter details page)
![deviceId-screenshot](https://github.com/FriendlyUser1/foxess-fetch/assets/41965390/3b4d407f-e49f-416f-99f8-4c3502459f78)
- Leave the token, it will be changed automatically
- Turn any of the variables you don't want data for to 0

In the console:
- Run `pip install -r ./requirements.txt`
- Run `python ./index.py`

## Done!
And that's it! 
On running the script you will recieve an object with data in 5 minute intervals of the past hour.

If you run into any errors, or need different features/time scales, please [open an issue](https://github.com/FriendlyUser1/foxess-fetch/issues/new).
