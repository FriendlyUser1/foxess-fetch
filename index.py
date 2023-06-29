import json
import hashlib
import requests
from datetime import datetime

from random_user_agent.user_agent import UserAgent

USER_AGENT = UserAgent(
    software_names=["chrome", "firefox"],
    operating_systems=["windows", "macos"],
    popularity=["very common"],
    software_types=["browser -> web-browser"],
    limit=1,
)
CONFIG_FILE = "config.json"
TEST_ENDPOINT = "https://www.foxesscloud.com/c/v0/plant/status/all"
AUTH_ENDPOINT = "https://www.foxesscloud.com/c/v0/user/login"
DATA_ENDPOINT = "https://www.foxesscloud.com/c/v0/device/history/raw"


def get_headers():
    user_agent = USER_AGENT.get_random_user_agent()
    return {
        "User-Agent": user_agent,
        "Accept": "application/json, text/plain, */*",
        "lang": "en",
        "Referer": "https://www.foxesscloud.com/",
    }


# Load and validate secrets from config.json
def load_config():
    try:
        with open(CONFIG_FILE) as cf:
            config = json.load(cf)
        if config["username"] and config["password"] and config["device_id"]:
            return config
    except:
        return None


# Load data variables from config.json
def load_variables():
    try:
        with open(CONFIG_FILE) as vf:
            vars = json.load(vf)["data_variables"]
        selected = []
        for var in vars:
            if vars[var] == 1:
                selected.append(var)

        if len(selected) > 0:
            return selected

    except:
        return None


# Cache a currently valid token to reduce later requests
def cache_token(token):
    with open(CONFIG_FILE) as cfr:
        config = json.load(cfr)
    config["token"] = token
    with open(CONFIG_FILE, "w") as cfw:
        json.dump(config, cfw, indent=2)


# Load the cached token
def load_cached_token():
    with open(CONFIG_FILE) as cf:
        return json.load(cf)["token"]


# Test the token with a light request
def test_token(headers):
    test_request = requests.get(TEST_ENDPOINT, headers=headers)

    if test_request.text is None:
        return False

    res = test_request.json()

    if res["result"] and res["errno"] == 0:
        return True

    return False


# Authenticate and recieve token for further requests
def auth(username, password, headers):
    auth_payload = f"user={username}&password={password}"

    auth_request = requests.post(AUTH_ENDPOINT, auth_payload, headers=headers)

    if auth_request.text is None:
        return print("Unable to authenticate - no data recieved")

    res = auth_request.json()

    if res["result"] is None:
        if res["errno"] == 41807:
            print(f"Unable to authenticate - bad username or password.")
        elif res["errno"] != 0:
            print(f"Unable to authenticate - {res}")
        else:
            print(f"Error communicating with API - {res}")

        return

    if auth_request.status_code != 200:
        return print(f"Error ${auth_request.status_code}")

    return res["result"]["token"]


# Get the actual data from the device
def get_data(device_id, headers, variables):
    now = datetime.now()

    payload = f'{{"deviceID":"{device_id}","variables":{variables},"timespan":"hour","beginDate":{{"year":{now.year},"month":{now.month},"day":{now.day},"hour":{now.hour}}}}}'

    data_request = requests.post(DATA_ENDPOINT, payload, headers=headers)

    if data_request.text is None:
        return print("No device data recieved")

    res = data_request.json()

    if res["result"] is None or res["errno"] != 0:
        return print("Error fetching data")

    return res["result"][0]


def main():
    config = load_config()
    variables = load_variables()

    if not config:
        return print("config.json is missing required properties")

    if not variables:
        return print("data_variables.json is missing required properties")

    username = config["username"]
    password = hashlib.md5(config["password"].encode()).hexdigest()
    device_id = config["device_id"]
    headers = get_headers()

    token = load_cached_token()
    if not test_token(headers | {"token": token}):
        token = auth(username, password, headers)
        cache_token(token)

    if not token:
        return

    data = get_data(
        device_id,
        headers | {"token": token},
        str(variables).replace("'", '"').replace(" ", ""),
    )

    return data


print(main())
