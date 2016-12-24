import decimal
import iso8601
import itertools
import aiohttp
import asyncio

from challonge.tournaments import Tournaments
from challonge.participants import Participants
from challonge.matches import Matches
from challonge.attachments import Attachments

try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree


CHALLONGE_API_URL = "api.challonge.com/v1"


class ChallongeException(Exception):
    pass


class Account():
    def __init__(self, username, api_key, loop=None):
        self._user = username
        self._api_key = api_key
        self._tournaments = Tournaments(self)
        self._participants = Participants(self)
        self._matches = Matches(self)
        self._attachments = Attachments(self)
        self._loop = loop or asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=self._loop)

    def __del__(self):
        self._session.close()

    @property
    def tournaments(self):
        return self._tournaments

    @property
    def participants(self):
        return self._participants

    @property
    def matches(self):
        return self._matches

    @property
    def attachments(self):
        return self._attachments

    @property
    async def is_valid(self):
        t = await self.fetch("GET", "tournaments")
        return t != ''

    async def fetch(self, method, uri, params_prefix=None, **params):
        """Fetch the given uri and return the contents of the response."""
        params = self._prepare_params(params, params_prefix)

        # build the HTTP request and use basic authentication
        url = "https://%s/%s.xml" % (CHALLONGE_API_URL, uri)

        with aiohttp.Timeout(60):
            async with self._session.request(method, url, params=params, auth=aiohttp.BasicAuth(self._user, self._api_key)) as response:
                resp = await response.text()
                if response.status >= 400:
                    raise ChallongeException(response.reason)
                return resp
        return None

    async def fetch_and_parse(self, method, uri, params_prefix=None, **params):
        """Fetch the given uri and return the root Element of the response."""
        doc = ElementTree.fromstring(await self.fetch(method, uri, params_prefix, **params))
        return self._parse(doc)

    def _parse_type(self, element):
        """ Determines and element type """
        element_type = element.get("type") or "string"

        if element.get("nil"):
            value = None
        elif element_type == "boolean":
            value = True if element.text.lower() == "true" else False
        elif element_type == "dateTime":
            value = iso8601.parse_date(element.text)
        elif element_type == "decimal":
            value = decimal.Decimal(element.text)
        elif element_type == "integer":
            value = int(element.text)
        elif element_type == "array":
            value = [self._parse(child) for child in element]
        else:
            value = element.text
        return value

    def _parse(self, root):
        """Recursively convert an Element into python data types"""
        if root.tag == "nil-classes":
            return []
        elif root.get("type") == "array":
            return [self._parse(child) for child in root]

        d = {}
        if len(root) == 0:
            value = self._parse_type(root)
            return value
        for child in root:
            d[child.tag] = self._parse_type(child)
        return d

    def _prepare_params(self, dirty_params, prefix=None):
        """Prepares parameters to be sent to challonge.com.

        The `prefix` can be used to convert parameters with keys that
        look like ("name", "url", "tournament_type") into something like
        ("tournament[name]", "tournament[url]", "tournament[tournament_type]"),
        which is how challonge.com expects parameters describing specific
        objects.

        """
        if prefix and prefix.endswith('[]'):
            keys = []
            values = []
            for k, v in dirty_params.items():
                if isinstance(v, (tuple, list)):
                    keys.append(k)
                    values.append(v)
            firstiter = ((k, v) for vals in zip(*values)
                         for k, v in zip(keys, vals))
            lastiter = ((k, v)
                        for k, v in dirty_params.items() if k not in keys)
            dpiter = itertools.chain(firstiter, lastiter)
        else:
            dpiter = dirty_params.items()

        params = []
        for k, v in dpiter:
            if isinstance(v, (tuple, list)):
                for val in v:
                    val = self._prepare_value(val)
                    if prefix:
                        params.append(("%s[][%s]" % (prefix, k), val))
                        # params["%s[%s]" % (prefix, k)] = v
                    else:
                        params.append((k + "[]", val))
                        # params[k] = v
            else:
                v = self._prepare_value(v)
                if prefix:
                    params.append(("%s[%s]" % (prefix, k), v))
                else:
                    params.append((k, v))

        return params

    def _prepare_value(self, val):
        if hasattr(val, "isoformat"):
            val = val.isoformat()
        elif isinstance(val, bool):
            # challonge.com only accepts lowercase true/false
            val = str(val).lower()
        return val
