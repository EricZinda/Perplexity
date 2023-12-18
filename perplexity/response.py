import enum


class ResponseLocation(enum.IntEnum):
    first = 0,
    middle = 1,
    last = 2


class RespondOperation(object):
    def __init__(self, response, location=ResponseLocation.middle, show_if_has_more=None):
        self._response = response
        self.response_location = location
        self._show_if_has_more = show_if_has_more

    def apply_to(self, state):
        pass

    def response_string(self, has_more):
        if self._show_if_has_more is None or (has_more == self._show_if_has_more):
            return self.response_location, self._response
