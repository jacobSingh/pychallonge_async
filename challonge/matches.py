class Matches():
    def __init__(self, account):
        self._account = account

    def index(self, tournament, **params):
        """Retrieve a tournament's match list."""
        return self._account.fetch_and_parse(
            "GET",
            "tournaments/%s/matches" % tournament,
            **params)


    def show(self, tournament, match_id):
        """Retrieve a single match record for a tournament."""
        return self._account.fetch_and_parse(
            "GET",
            "tournaments/%s/matches/%s" % (tournament, match_id))


    def update(self, tournament, match_id, **params):
        """Update/submit the score(s) for a match."""
        self._account.fetch(
            "PUT",
            "tournaments/%s/matches/%s" % (tournament, match_id),
            "match",
            **params)
