import logging


def Predication(vocabulary, name=None, synonyms=[]):
    # Gets called when the function is first created
    # function_to_decorate is the function definition
    def PredicationDecorator(function_to_decorate):
        def wrapper_function(*args, **kwargs):
            # For now just iterate from the predication,
            # later we'll do more here
            yield from function_to_decorate(*args, **kwargs)

        predication_name = name if name is not None else function_to_decorate.__name__
        vocabulary.add_predication(function_to_decorate.__module__, function_to_decorate.__name__, predication_name, synonyms)

        return wrapper_function

    return PredicationDecorator


class Vocabulary(object):
    def __init__(self):
        self.all = dict()

    def add_predication(self, module, function, delphin_name, synonyms):
        self.all[delphin_name] = [module, function]
        for synonym in synonyms:
            self.all[synonym] = [module, function]

    def predication(self, delphin_name):
        return self.all.get(delphin_name, None)


pipeline_logger = logging.getLogger('Pipeline')
