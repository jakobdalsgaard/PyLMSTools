"""
Example of querying the RPC interface using simple HTTP
requests using the python requests package

Interface documentation available at:
https://lyrion.org/reference/cli/using-the-cli/#jsonrpcjs

"""
import sys
import pprint
from uuid import uuid4
import requests


def lms_request(params_list: list, server_url='http://127.0.0.1:9000/jsonrpc.js'):
    """
    Function to construct and make HTTP POST requests to the LMS RPC interface
    and parse the response
    """
    # Construct the request payload as a dict that will be converted to JSON
    request_payload = {"id": str(uuid4()),
               "method": "slim.request",
               "params": params_list,
               }
    try:
        # All requests to the interface are HTTP POST
        response = requests.post(url=server_url, json=request_payload, timeout=3)
    except requests.exceptions.ConnectTimeout:
        # The server did not respond after the given timeout
        print('timeout')
        response = None
    except requests.exceptions.ConnectionError:
        # The server returned a null response. Seems to be how the interface responds to
        # an invalid request
        print('server returned null')
        response = None

    if response:
        if response.status_code == 200:
            # The server response comprises of the request parameters with a 'result'
            # item appended so just return the 'result'
            return response.json()['result']
        # Not sure if the interface returns anything other than 200-OK
        print(f"{response.status_code=}, {response.text=}")
    return None


url = sys.argv[1]

# Get the number of players connected to the server
payload = ["", ["player", "count", "?"]]
resp = lms_request(params_list=payload, server_url=url)
player_count = resp['_count']
print(f"{player_count=}")

# Get connected players' detail in a single call
payload = ["", ["players", 0, int(player_count)]]
resp = lms_request(params_list=payload, server_url=url)
pprint.pprint(resp)

# Print some attributes of each player
for i in range(int(player_count)):
    print('*' * 10)
    payload = ["", ["player", "id", i, "?"]]
    resp = lms_request(params_list=payload, server_url=url)
    player_mac = resp['_id']
    print(f"{player_mac=}")

    payload = ["", ["player", "name", i, "?"]]
    resp = lms_request(params_list=payload, server_url=url)
    player_name = resp['_name']
    print(f"{player_name=}")

    payload = ["", ["player", "ip", i, "?"]]
    resp = lms_request(params_list=payload, server_url=url)
    player_ip = resp['_ip']
    print(f"{player_ip=}")

    payload = [player_mac, ["mixer", "volume", "?"]]
    resp = lms_request(params_list=payload, server_url=url)
    player_vol = resp['_volume']
    print(f"{player_vol=}")

    payload = [player_mac, ["title", "?"]]
    resp = lms_request(params_list=payload, server_url=url)
    # resp wil be an empty dict if no track selected
    player_track_title = resp.get('_title', '')
    print(f"{player_track_title=}")

    payload = [player_mac, ["artist", "?"]]
     # resp wil be an empty dict if no track selected
    player_track_artist = resp.get('_artist', '')
    print(f"{player_track_artist=}")

    payload = [player_mac, ["album", "?"]]
    # resp wil be an empty dict if no track selected
    player_track_album = resp.get('_album', '')
    print(f"{player_track_album=}")

    payload = [player_mac, ["current_title", "?"]]
    # resp wil be an empty dict if no track selected
    player_track_current_title = resp.get('_current_title', '')
    print(f"{player_track_current_title=}")

    payload = [player_mac, ["path", "?"]]
    # resp wil be an empty dict if no track selected
    player_track_path = resp.get('_path', '')
    print(f"{player_track_path=}")
