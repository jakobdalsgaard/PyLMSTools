"""
Simple python class definitions for interacting with Logitech Media Server.
This code uses the JSON RPC interface.
"""
import logging
from typing import List
import requests
from pylmstools.player import LMSPlayer


LOG = logging.getLogger()

class LMSConnectionError(Exception):
    """
    Exception raised when a connection to the LMS server cannot be made
    """

class LMSServerError(Exception):
    """
    Exception raised when a server request fails
    """


class LMSServer():
    """
    :type host: str
    :param host: address of LMS server (default "localhost")
    :type port: int
    :param port: port for the web interface (default 9000)

    Class for Logitech Media Server.
    Provides access via JSON interface. As the class uses the JSON interface,
    no active connections are maintained.

    """

    def __init__(self, host="localhost", port=9000):
        self.host = host
        self.port = port
        self._version = None
        self.id = 1
        self.web = f"http://{host}:{port}/"
        self.url = f"http://{host}:{port}/jsonrpc.js"
        self.players = None

    def request(self, player="", params=None):
        """
        :type player: (str)
        :param player: MAC address of a connected player. Alternatively, 
                       "-" can be used for server level requests.
        :type params: (str, list)
        :param params: Request command

        """
        if params is None:
            params = []

        LOG.debug('server request: %s %s %s', self.url, player, params)

        cmd = [player, params]

        payload = {"id": self.id,
                "method": "slim.request",
                "params": cmd}

        LOG.debug('Request payload: %s', payload)
        try:
            response = requests.post(url=self.url, json=payload, timeout=10)
        except requests.exceptions.ConnectTimeout as err:
            raise LMSConnectionError("Could not connect to server.") from err
        except requests.exceptions.ConnectionError as err:
            raise LMSServerError("Null response - likely problem with request") from err

        if response.status_code == 200:
            return response.json()['result']

        LOG.error("%s - %s", response.status_code, response.text)
        return None

    def get_players(self) -> List[LMSPlayer]:
        """
        :rtype: list
        :returns: list of LMSPlayer instances

        Return a list of currently connected Squeezeplayers.
        ::

            >>>server.get_players()
            [LMSPlayer: Living Room (40:40:40:40:40:40),
             LMSPlayer: PiRadio (41:41:41:41:41:41),
             LMSPlayer: elParaguayo's Laptop (42:42:42:42:42:42)]

        """
        self.players = []
        player_count = self.get_player_count()
        for i in range(player_count):
            player = LMSPlayer.from_index(i, self)
            self.players.append(player)
        return self.players

    def get_player_count(self) -> int:
        """
        :rtype: int
        :returns: number of connected players

        ::

            >>>server.get_player_count()
            3

        """
        count = self.request(params=["player", "count", "?"])["_count"]

        return count

    def get_sync_groups(self) -> List:
        """
        :rtype: list
        :returns: list of syncgroups. Each group is a list of references of the members.

        ::

            >>>server.get_sync_groups()
            [[u'40:40:40:40:40:40', u'41:41:41:41:41:41']]

        """
        groups = self.request(params="syncgroups ?")
        syncgroups = [x.get("sync_members","").split(",") for x in groups.get("syncgroups_loop", {})]
        return syncgroups

    def show_players_sync_status(self) -> dict:
        """
        :rtype: dict
        :returns: dictionary (see attributes below)
        :attr group_count: (int) Number of sync groups
        :attr player_count: (int) Number of connected players
        :attr players: (list) List of players (see below)

        Player object (dict)

        :attr name: Name of player
        :attr ref: Player reference
        :attr sync_index: Index of sync group (-1 if not synced)

        ::

            >>>server.show_players_sync_status()
            {'group_count': 1,
             'player_count': 3,
             'players': [{'name': u'Living Room',
                          'ref': u'40:40:40:40:40:40',
                          'sync_index': 0},
                          {'name': u'PiRadio',
                          'ref': u'41:41:41:41:41:41',
                          'sync_index': 0},
                          {'name': u"elParaguayo's Laptop",
                          'ref': u'42:42:42:42:42:42',
                          'sync_index': -1}]}

        """
        players = self.get_players()
        groups = self.get_sync_groups()

        all_players = []

        for player in players:
            item = {}
            item["name"] = player.name
            item["ref"] = player.ref
            index = [i for i, g in enumerate(groups) if player.ref in g]
            if index:
                item["sync_index"] = index[0]
            else:
                item["sync_index"] = -1
            all_players.append(item)

        sync_status = {}
        sync_status["group_count"] = len(groups)
        sync_status["player_count"] = len(players)
        sync_status["players"] = all_players

        return sync_status

    def sync(self, master, slave):
        """
        :type master: (ref)
        :param master: Reference of the player to which you wish to sync another player
        :type slave: (ref)
        :param slave: Reference of the player which you wish to sync to the master

        Sync squeezeplayers.
        """
        self.request(player=master, params=["sync", slave])


    def ping(self) -> bool:
        """
        :rtype: bool
        :returns: True if server is alive, False if server is unreachable

        Method to test if server is active.

        ::

            >>>server.ping()
            True

        """
        # 'ping' is not a valid interface command so a 'null' result will
        # indicate that the server is reachable
        try:
            self.request(params=["ping"])
        except LMSServerError:
            pass
        except LMSConnectionError:
            return False
        return True

    @property
    def version(self) -> str:
        """
        :attr version: Version number of server Software

        ::

            >>>server.version
            u'7.9.0'
        """
        if self._version is None:
            self._version = self.request(params=["version", "?"])["_version"]
        return self._version

    def rescan(self, mode='fast'):
        """
        :type mode: str
        :param mode: Mode can be 'fast' for update changes on library, 'full' for complete
                     library scan and 'playlists' for playlists scan only

        Trigger rescan of the media library.
        """

        is_scanning = bool(self.request(["rescan", "?"])["_rescan"])

        if not is_scanning:
            if mode == 'fast':
                return self.request(params=["rescan"])
            if mode == 'full':
                return self.request(params=["wipecache"])
            if mode == 'playlists':
                return self.request(params=["rescan", "playlists"])

        return ""

    @property
    def rescanprogress(self):
        """
        :attr rescanprogress: current rescan progress
        """
        return self.request(params=["rescanprogress"])["_rescan"]
