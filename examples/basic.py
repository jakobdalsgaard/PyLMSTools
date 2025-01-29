"""
Script showing basic usage of the PyLMSTools package
"""
import logging
from pylmstools.server import LMSServer


if __name__ == '__main__':
    local_server = LMSServer(host='192.168.55.105')
    print(f"{local_server.ping()=}")
    print(f"{local_server.version=}")
    print(f"{local_server.get_player_count()=}")
    print(f"{local_server.get_players()=}")
    for player in local_server.get_players():
        print(f" {player.mode=}")
        print(f" {player.volume=}")
        print(f" {player.current_title=}")
        print(f" {player.track_title=}")
        print(f" {player.track_artist=}")
        print(f" {player.track_album=}")
        print(f" {player.track_count=}")
        print(f" {player.track_duration=}")
        print(f" {player.track_elapsed_and_duration=}")
        print(f" {player.time_remaining=}")
        print(f" {player.playlist_position=}")
        print(f" {player.percentage_elapsed()=}")
        print(f" {player.get_synced_players()=}")
