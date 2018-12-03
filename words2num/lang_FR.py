from __future__ import division, unicode_literals, print_function
import re
from .core import NumberParseException, placevalue
import difflib

VOCAB = {
    'zero': (0, 'Z'),
    'et': (None, 'A'),
    'un': (1, 'D'),
    'deux': (2, 'D'),
    'trois': (3, 'D'),
    'quatre': (4, 'D'),
    'cinq': (5, 'D'),
    'six': (6, 'D'),
    'sept': (7, 'D'),
    'huit': (8, 'D'),
    'neuf': (9, 'D'),
    'dix': (10, 'M'),
    'onze': (11, 'M'),
    'douze': (12, 'M'),
    'treize': (13, 'M'),
    'quatorze': (14, 'M'),
    'quinze': (15, 'M'),
    'seize': (16, 'M'),
    'dix-sept': (17, 'M'),
    'dix-huit': (18, 'M'),
    'dix-neuf': (19, 'M'),
    'vingt': (20, 'T'),
    'trente': (30, 'T'),
    'quarante': (40, 'T'),
    'cinquante': (50, 'T'),
    'soixante': (60, 'T'),
    'septante': (70, 'T'),
    'octante': (80, 'T'),
    'huitante': (80, 'T'),
    'nonante': (90, 'T'),
    'cent': (100, 'H'),
    'mille': (10 ** 3, 'X'),
    'million': (10 ** 6, 'X'),
    'milliard': (10 ** 9, 'X'),
    'billion': (10 ** 12, 'X'),
    'virgule': (None, 'V'),
    'moins': (None, '-'),
    'pi': (3.1415926535898, 'D')
}


class FST:
    def __init__(self):
        def f_zero(self, n):
            assert n == 0
            self.value = n

        def f_add(self, n):
            self.value += n

        def f_mul(self, n):
            if self.value == 0:
                self.value = 1
            output = self.value * n
            self.value = 0
            return output

        def f_mul_hundred(self, n):
            assert n == 100
            self.value *= n

        def f_ret(self, _):
            return self.value

        def f_none(self, _):
            pass

        def f_hundred(self, n):
            assert n == 100
            self.value = n

        def f_frenchy_80(self, n):
            assert n == 20
            self.value = self.value - 4 + 80

        def f_frenchy_70_90(self, n):
            assert n >= 10 and n < 20
            self.value += n

        def f_frenchy_17_19(self, n):
            assert n >= 7 and n <= 9
            self.value += n

        self.value = 0
        self.state = 'S'
        # self.states = {'S', 'D', 'T', 'M', 'H', 'X', 'Z', 'A', 'F'}
        self.edges = {
            ('S', 'Z'): f_zero,    # 0
            ('S', 'D'): f_add,     # 9
            ('S', 'T'): f_add,     # 90
            ('S', 'M'): f_add,     # 19
            ('S', 'H'): f_add,     # 100
            ('S', 'X'): f_mul,     # 1000
            ('S', 'A'): f_none,    # 100
            ('D', 'H'): f_mul_hundred,     # 900
            ('D', 'X'): f_mul,     # 9000
            ('D', 'F'): f_ret,     # 9
            ('T', 'D'): f_add,     # 99
            ('T', 'H'): f_mul_hundred,
            ('T', 'X'): f_mul,     # 90000
            ('T', 'F'): f_ret,     # 90
            ('M', 'H'): f_mul_hundred,
            ('M', 'X'): f_mul,     # 19000
            ('M', 'F'): f_ret,     # 19
            ('H', 'D'): f_add,     # 909
            ('H', 'T'): f_add,     # 990
            ('H', 'M'): f_add,     # 919
            ('H', 'X'): f_mul,     # 900000
            ('H', 'F'): f_ret,     # 900
            ('X', 'D'): f_add,     # 9009
            ('X', 'T'): f_add,     # 9090
            ('X', 'M'): f_add,     # 9019
            ('X', 'H'): f_add,     # 9100
            ('X', 'F'): f_ret,     # 9000
            ('X', 'X'): f_add,     # 1000100
            ('Z', 'F'): f_ret,     # 0
            ('A', 'H'): f_hundred,  # 100
            ('D', 'T'): f_frenchy_80,  # 80
            ('T', 'M'): f_frenchy_70_90,  # 79-99
            ('M', 'D'): f_frenchy_17_19  # 17-19
        }

    def transition(self, token):
        value, label = token
        try:
            edge_fn = self.edges[(self.state, label)]
        except KeyError:
            raise NumberParseException("Invalid number state from "
                                       "{0} to {1}".format(self.state, label))
        self.state = label
        return edge_fn(self, value)


def tokenize(text):
    tokens = re.split(r"[\s,\-]+(?:et)?", text.lower())
    try:
        # don't use generator here because we want to raise the exception
        # here now if the word is not found in vocabulary (easier debug)
        # parsed_tokens = [VOCAB[token] for token in tokens if token]
        parsed_tokens = [VOCAB[difflib.get_close_matches(token, VOCAB.keys(), n=1, cutoff=0)[0]] for token in tokens if token]
    except KeyError as e:
        raise ValueError("Invalid number word: "
                         "{0} in {1}".format(e, text))
    return parsed_tokens


def compute(tokens):
    """Compute the value of given tokens.
    TODO: memoize placevalue checking at every step
    """
    fst = FST()
    outputs = []
    last_placevalue = None
    for token in tokens:
        out = fst.transition(token)
        # DEBUG
        # print("tok({0}) out({1}) val({2})".format(token, out, fst.value))
        if out:
            outputs.append(out)
            if last_placevalue and last_placevalue <= placevalue(outputs[-1]):
                raise NumberParseException("Invalid sequence "
                                           "{0}".format(outputs))
            last_placevalue = placevalue(outputs[-1])
    outputs.append(fst.transition((None, 'F')))
    if last_placevalue and last_placevalue <= placevalue(outputs[-1]):
        raise NumberParseException("Invalid sequence "
                                   "{0}".format(outputs))
    # DEBUG
    # print("-> {0}".format(outputs))
    return sum(outputs)


def compute_after_coma(tokens):
    i = 0
    while (tokens[i] ==(0, 'Z')):
        i += 1

    return "0" * i + str(compute(tokens[i:]))

def evaluate(text):
    tokens = tokenize(text)
    if not tokens:
        raise ValueError("No valid tokens in {0}".format(text))

    if tokens[0] == (None, '-'):
        sign = -1
        tokens = tokens[1:]
    else:
        sign = 1

    coma_token = (None, 'V')
    if coma_token in tokens:
        before_coma = tokens[:(tokens.index(coma_token))]
        after_coma = tokens[tokens.index(coma_token) + 1:]

        return sign * eval(str(compute(before_coma)) + "." + compute_after_coma(after_coma))
    else:
        return sign * compute(tokens)
