import json

from happi import Client
from happi.backends.json_db import JSONBackend
from happi.backends.core import ItemMeta


class RawJSONBackend(JSONBackend):
    def __init__(
        self,
        raw_json: str,
        initialize: bool = False
    ) -> None:
        '''
        Wrapper to use raw json data to load devices in happi
        Args:
            raw_json:       Raw json data
        '''
        self._load_cache: dict[str, ItemMeta] = None
        self.raw_json = raw_json
        if initialize:
            self.initialize()
        pass

    def load(self):
        '''
        Load the JSON raw data
        '''
        return json.loads(self.raw_json)


class RawJSONClient(Client):
    def __init__(self, raw_json, **kwargs):
        '''
        Wrapper to use a raw json data loader as happi's backend
        Args:
            raw_json:       Raw json data
        '''
        self._retain_cache = False
        self.backend = RawJSONBackend(raw_json=raw_json, **kwargs)
        pass
