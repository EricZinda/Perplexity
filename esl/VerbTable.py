class StructuredVerb(object):
    def __init__(self, lemma, arg_struct):
        self.lemma = lemma
        self.arg_struct = arg_struct

    def __eq__(self, other):
        return self.lemma == other.lemma and self.arg_struct == other.arg_struct

    def __hash__(self):
        return hash(self.lemma + "".join(self.arg_struct))


class VerbTable(object):
    def __init__(self):
        self.table = {}

    def add(self, lemma, arg_struct, func):
        self.table[StructuredVerb(lemma, arg_struct)] = func

    def lookup(self, lemma, arg_struct):
        verb = StructuredVerb(lemma, arg_struct)
        if verb in self.table.keys():
            return self.table[verb]
        else:
            return None
