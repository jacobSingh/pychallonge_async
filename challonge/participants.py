class Participants():
    def __init__(self, account):
        self._account = account

    def index(self, tournament):
        """Retrieve a tournament's participant list."""
        return self._account.fetch_and_parse(
            "GET",
            "tournaments/%s/participants" % tournament)


    def create(self, tournament, name, **params):
        """Add a participant to a tournament."""
        params.update({"name": name})

        return self._account.fetch_and_parse(
            "POST",
            "tournaments/%s/participants" % tournament,
            "participant",
            **params)


    def bulk_add(self, tournament, names, **params):
        """Bulk add participants to a tournament (up until it is started).

        :param tournament: the tournament's name or id
        :param names: the names of the participants
        :type tournament: int or string
        :type names: list or tuple
        :return: each participants info
        :rtype: a list of dictionaries

        """
        params.update({"name": names})

        return self._account.fetch_and_parse(
            "POST",
            "tournaments/%s/participants/bulk_add" % tournament,
            "participants[]",
            **params)


    def show(self, tournament, participant_id):
        """Retrieve a single participant record for a tournament."""
        return self._account.fetch_and_parse(
            "GET",
            "tournaments/%s/participants/%s" % (tournament, participant_id))


    def update(self, tournament, participant_id, **params):
        """Update the attributes of a tournament participant."""
        self._account.fetch(
            "PUT",
            "tournaments/%s/participants/%s" % (tournament, participant_id),
            "participant",
            **params)


    def check_in(self, tournament, participant_id):
        """Checks a participant in."""
        self._account.fetch(
            "POST",
            "tournaments/%s/participants/%s/check_in" % (tournament, participant_id))


    def undo_check_in(self, tournament, participant_id):
        """Marks a participant as having not checked in."""
        self._account.fetch(
            "POST",
            "tournaments/%s/participants/%s/undo_check_in" % (tournament, participant_id))


    def destroy(self, tournament, participant_id):
        """Destroys or deactivates a participant.

        If tournament has not started, delete a participant, automatically
        filling in the abandoned seed number.

        If tournament is underway, mark a participant inactive, automatically
        forfeiting his/her remaining matches.

        """
        self._account.fetch(
            "DELETE",
            "tournaments/%s/participants/%s" % (tournament, participant_id))


    def randomize(self, tournament):
        """Randomize seeds among participants.

        Only applicable before a tournament has started.

        """
        self._account.fetch("POST", "tournaments/%s/participants/randomize" % tournament)
