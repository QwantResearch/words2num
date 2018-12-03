import unittest
import random
import sys
from multiprocessing import Process
from words2num import words2num, NumberParseException
from num2words import num2words


class TestFR(unittest.TestCase):
    """Test inverse text normalization for numbers.
    """

    def test_fr(self):
        """Test valid fr input.
        """
        test_trials = ("deux",
            "douze",
            "vingt-et-un",
            "zero",
            "cent deux",
            "cent vingt trois",
            "mille cent un",
            "trois mille quatre cent cinquante six",
            "deux cent mille trois cent quarante cinq",
            "deux millions trois cents mille quatre",
            "soixante huit milliards deux cents deux millions et deux",
            "zéro virgule cinq",
            "moins trois cent quatre vingts dix virgule cinquante deux",
            "moins soixante-dix-huit",
            "quatre-vingts treize",
            "un virgule zero zero trois")
        test_targets = (2,
                        12,
                        21,
                        0,
                        102,
                        123,
                        1101,
                        3456,
                        200345,
                        2300004,
                        68202000002,
                        0.5,
                        -390.52,
                        -78,
                        93,
                        1.003)
        tests = zip(test_trials, test_targets)

        for (trial, target) in tests:
            result = words2num(trial, lang="fr")
            assert result == target,\
                   "'{0}' -> {1} != {2}".format(trial, result, target)


    @unittest.skipIf(sys.version_info[0] < 3, 'python2 fails at concurrency')
    def test_fr_auto(self):
        """Test many (valid) inputs sampled from a wide range.
        Inputs are created by num2word.
        """
        def inv_test(n):
            words = make_words(n)
            result = words2num(words, lang="fr")
            assert n == result,\
                   "{0} ({1}) inverted as {3}".format(n, words, result)

        def make_words(n):
            if n % 1 != 0:
                # Float case
                words = num2words(round(n - n%1, 4), lang="fr") + " virgule "
                float_part = round(n % 1, 4)
                zeros = 0
                while round(float_part % 1, 4) not in [0, 1]:
                    float_part *= 10
                    if (float_part // 1) == 0:
                        zeros += 1
                words += "zero " * zeros + num2words(round(float_part), lang="fr")
                return words
            return num2words(n, lang="fr")

        def float_range(int_range):
            return [x / 10000.0 for x in int_range]

        def test_numbers():
            _step = 64
            for start_i in random.sample(range(99999999999), 64):
                plist = [Process(target=inv_test, args=(n,))\
                         for n in range(start_i, start_i + _step)]
                for p in plist:
                    p.start()
                for p in plist:
                    p.join()

        def test_numbers_coma():
            _step = 64
            for start_i in random.sample(range(99999), 64):
                plist = [Process(target=inv_test, args=(n,))\
                         for n in float_range(range(start_i, start_i + _step))]
                for p in plist:
                    p.start()
                for p in plist:
                    p.join()

        test_numbers()
        test_numbers_coma()

    def test_fr_neg(self):
        """Test invalid fr input.
        Ensure that invalid number sequences raise NumberParseException.
        """
        tests = ("huit dix",
                 "un un",
                 # "cinquante dix huit", For now, there is no way to make it fail
                 "un million cent un un",
                 # "mille cent millions", For now, there is no way to make it fail
                 "vingt zéro",
                 "zéro virgule un virgule un",
                 "moins moins un",
                 "un virgule zero cinq zero",
                 # "cinq vingts", For now, there is no way to make it fail
                 )

        for test in tests:
            try:
                value = words2num(test, lang="fr")
                assert False,\
                       "parsed invalid input '{0}' as {1}".format(test, value)
            except NumberParseException:
                pass

        tests = (
            "soixante-dix-trois",
            "quantre-vingt-dix-cinq",
        )

        for test in tests:
            try:
                words2num(test, lang="fr")
                assert False,\
                       "assert n >= 7 and n <= 9"
            except AssertionError:
                pass



if __name__ == '__main__':
    unittest.main()
