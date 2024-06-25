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
        return self.response_string(state=None, has_more=(True if self.show_if_has_more else False))

    def apply_to(self, state):
        pass

    def response_string(self, state, has_more):
        if self.show_if_has_more is None or (has_more == self.show_if_has_more):
            return self.response_location, self._response


# This is designed to give a prompt based on the current state
class RepromptOperation(RespondOperation):
    def __init__(self, location=ResponseLocation.middle, show_if_has_more=None, show_if_last_phrase=None):
        super().__init__("", location=location, show_if_has_more=show_if_has_more, show_if_last_phrase=show_if_last_phrase)

    def __repr__(self):
        return self.response_string(None, has_more=(True if self.show_if_has_more else False))

    def apply_to(self, state):
        pass

    def response_string(self, state, has_more):
        if self.show_if_has_more is None or (has_more == self.show_if_has_more):
            if state is not None:
                reprompt_text = state.get_reprompt(return_first=False)
            else:
                reprompt_text = "current state"

        return self.response_location, reprompt_text


def get_reprompt_operation(state, use_blank_response=False):
    return RepromptOperation(location=ResponseLocation.last, show_if_last_phrase=True)
