import os
import unittest

if __name__ == '__main__':

    tests_dir = os.path.dirname(os.path.realpath(__file__))

    suite = unittest.TestSuite()
    all_cases = unittest.defaultTestLoader.discover(tests_dir, pattern='test_*.py')
    for case in all_cases:
        suite.addTests(case)

    runner = unittest.TextTestRunner()
    runner.run(suite)