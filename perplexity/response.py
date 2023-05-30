import enum

import inflect


class RespondOperation(object):
    def __init__(self, response):
        self.response = response

    def apply_to(self, state):
        pass

    def response_string(self):
        return self.response


class PluralMode(enum.Enum):
    plural = 0,
    singular = 1,
    as_is = 2


# Objects that want to handle their own
# articles need to implement all of these methods
# class SayText(object):
#     def __init__(self, text):
#         self.text = text
#
#     def is_uncountable(self):
#         pass
#
#     def with_indefinite_article(self):
#         return p.an(self.text)
#
#     def plural(self, plural_mode):
#         if plural_mode == PluralMode.plural:
#             return p.plural(self.text)
#         elif plural_mode == PluralMode.singular:
#             return p.plural

# `word` should be singular with no determiner
class SayWord(object):
    def __init__(self, word):
        self.word = word
        self.uncountable = {"water"}

    def _is_uncountable(self):
        return self.word in self.uncountable

    def convert_to(self, determiner, plural_mode):
        if plural_mode == PluralMode.plural:
            phrase = p.plural(self.word)
        elif plural_mode == PluralMode.singular:
            phrase = self.word
        else:
            phrase = self.word

        if self._is_uncountable():
            determiner = None

        if determiner is None:
            return phrase
        elif determiner in ["a", "an"]:
            return p.an(phrase)
        else:
            return f"the {phrase}"


def capitalize(initial_cap, phrase):
    if initial_cap:
        return phrase.capitalize()
    else:
        return phrase


def s(determiner, o, plural=PluralMode.as_is, initial_cap=False, count=None):
    if isinstance(o, str):
        o = SayWord(o)

    if count is not None:
        assert plural == PluralMode.as_is, "If count is a number, plural must = PluralMode.as_is"
        plural = PluralMode.singular if count == 1 else PluralMode.plural

    return capitalize(initial_cap, o.convert_to(determiner, plural))


def is_plural_word(word):
    # Returns false if word is already singular
    return p.singular_noun(word) is not False


def change_to_plural_mode(singular_word, plural_mode):
    if plural_mode == PluralMode.singular:
        return singular_word
    elif plural_mode == PluralMode.plural:
        return p.plural(singular_word)
    else:
        return singular_word


p = inflect.engine()


if __name__ == '__main__':
    print(change_plural_mode("dog", PluralMode.plural))
    print(p.singular_noun('friend'))
    # # https://github.com/jaraco/inflect
    # print(f"There is {s('a', 'water')}")
    #
    # print(f"There is more than 1 {s('file', determiner=None, count=1)}")