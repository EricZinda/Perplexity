import enum


class ResponseLocation(enum.IntEnum):
    first = 0,
    middle = 1,
    last = 2


class NoopOperation(object):
    def apply_to(self, state):
        pass


class RespondOperation(object):
    def __init__(self, response, location=ResponseLocation.middle, show_if_has_more=None, show_if_last_phrase=None):
        self._response = response
        self.response_location = location
        self.show_if_has_more = show_if_has_more
        self.show_if_last_phrase = show_if_last_phrase

    def __repr__(self):
        return self.response_string(True if self.show_if_has_more else False)

    def apply_to(self, state):
        pass

    def response_string(self, has_more):
        if self.show_if_has_more is None or (has_more == self.show_if_has_more):
            return self.response_location, self._response


def get_reprompt_operation(state, use_blank_response=False):
    reprompt_text = state.get_reprompt(return_first=False)
    if reprompt_text is None or reprompt_text == "":
        if not use_blank_response:
            return NoopOperation()
        else:
            return RespondOperation("", location=ResponseLocation.last, show_if_last_phrase=True)
    else:
        return RespondOperation(reprompt_text, location=ResponseLocation.last, show_if_last_phrase=True)
