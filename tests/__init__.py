import unittest
import word2num


class TestITN(unittest.TestCase):
    """Test inverse text normalization for numbers.
    """

    def test_en_us(self):
        """Test postives for en-US.
        """
        test_trials = ("two",
            "twelve",
            "one hundred and two",
            "a hundred twenty-three",
            "two hundred thousand, three hundred forty five",
            "sixty-eight billion, two hundred two million and two",
            "sixty eight billion two hundred two million two",
            "nine trillion eight hundred seven")
        test_targets = (2,
            12,
            102,
            123,
            200345,
            68202000002,
            68202000002,
            9000000000807)
        tests = zip(test_trials, test_targets)

        for (trial, target) in tests:
            assert word2num.word2num(trial) == target


if __name__ == '__main__':
    unittest.main()