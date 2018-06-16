from __future__ import division, unicode_literals, print_function
import re
from .core import NumberParseException, placevalue

VOCAB = {
    'zero': (0, 'Z'),
    # 'e': (None, 'A'),
    'um': (1, 'D'),
    'dois': (2, 'D'),
    'três': (3, 'D'),
    'quatro': (4, 'D'),
    'cinco': (5, 'D'),
    'seis': (6, 'D'),
    'sete': (7, 'D'),
    'oito': (8, 'D'),
    'nove': (9, 'D'),
    'dez': (10, 'M'),
    'onze': (11, 'M'),
    'doze': (12, 'M'),
    'treze': (13, 'M'),
    'quatorze': (14, 'M'),
    'quinze': (15, 'M'),
    'dezesseis': (16, 'M'),
    'dezessete': (17, 'M'),
    'dezoito': (18, 'M'),
    'dezenove': (19, 'M'),
    'vinte': (20, 'T'),
    'trinta': (30, 'T'),
    'quarenta': (40, 'T'),
    'cinquenta': (50, 'T'),
    'sessenta': (60, 'T'),
    'setenta': (70, 'T'),
    'oitenta': (80, 'T'),
    'noventa': (90, 'T'),
    'cem': (100, 'H'),
    'cento': (100, 'H'),
    'duzentos': (200, 'X'),
    'trezentos': (300, 'X'),
    'quatrocentos': (400, 'X'),
    'quinhentos': (500, 'X'),
    'seiscentos': (600, 'X'),
    'setecentos': (700, 'X'),
    'oitocentos': (800, 'X'),
    'novecentos': (900, 'X'),
    'mil': (10 ** 3, 'X'),
    'milhão': (10 ** 6, 'X'),
    'milhões': (10 ** 6, 'X'),
    'bilhão': (10 ** 9, 'X'),
    'bilhões': (10 ** 9, 'X'),
    'trillion': (10 ** 12, 'X'),
    'quadrillion': (10 ** 15, 'X'),
    'quintillion': (10 ** 18, 'X'),
    'sextilião': (10 ** 21, 'X'),
    'septilhão': (10 ** 24, 'X'),
    'octillion': (10 ** 27, 'X'),
    'nonillion': (10 ** 30, 'X'),
    'decillion': (10 ** 33, 'X'),
    'undecillion': (10 ** 36, 'X'),
    'duodecilião': (10 ** 39, 'X'),
    'tredecillion': (10 ** 42, 'X'),
    'quattuordecillion': (10 ** 45, 'X'),
    'quindecillion': (10 ** 48, 'X'),
    'sexdecillion': (10 ** 51, 'X'),
    'septendecillion': (10 ** 54, 'X'),
    'octodecilião': (10 ** 57, 'X'),
    'novemdecillion': (10 ** 60, 'X'),
    'vigintillion': (10 ** 63, 'X'),
    'centillion': (10 ** 303, 'X'),
}

class FST:
    def __init__(self):
        def f_zero(self, n):
            assert n == 0
            self.value = n

        def f_add(self, n):
            self.value += n
        
        def f_add_str(self, n):
            tmp = str(self.value) + str(n)
            self.value = int(tmp)
            # self.value += ''+n

        def f_mul(self, n):
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

        self.value = 0
        self.state = 'S'
        # self.states = {'S', 'D', 'T', 'M', 'H', 'X', 'Z', 'A', 'F'}
        self.edges = {
            ('S', 'Z'): f_zero,    # 0
            ('S', 'D'): f_add,     # 9
            ('S', 'T'): f_add,     # 90
            ('S', 'M'): f_add,     # 19
            ('S', 'A'): f_none,    # 100
            ('S', 'H'): f_none,    # 200
            ('S', 'X'): f_add,     # 200
            ('D', 'H'): f_mul_hundred,     # 900
            ('D', 'X'): f_mul,     # 9000
            ('D', 'F'): f_ret,     # 9
            ('D', 'D'): f_add_str, # 9
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
            ('X', 'A'): f_add,     # 9100
            ('X', 'F'): f_ret,     # 9000
            ('Z', 'F'): f_ret,     # 0
            ('A', 'H'): f_hundred  # 100
        }

    def transition(self, token):
        value, label = token
        print(self.state, label)
        
        try:
            edge_fn = self.edges[(self.state, label)]
        except KeyError:
            raise NumberParseException("Invalid number state from "
                                       "{0} to {1}".format(self.state, label))
        self.state = label
        return edge_fn(self, value)


def tokenize(text):
    tokens = re.split(r"[\s,\-]+(?:e)?", text.lower())
    try:
        # don't use generator here because we want to raise the exception
        # here now if the word is not found in vocabulary (easier debug)
        parsed_tokens = [VOCAB[token] for token in tokens if token]
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
        # print("tok({0}) out({1})".format(token, fst.value))
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


def evaluate(text):
    tokens = tokenize(text)
    if not tokens:
        raise ValueError("No valid tokens in {0}".format(text))
    return compute(tokens)
