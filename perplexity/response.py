

class RespondOperation(object):
    def __init__(self, response):
        self.response = response

    def apply_to(self, state):
        pass

    def response_string(self):
        return self.response