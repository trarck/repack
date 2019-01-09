import unittest

from actions.file_actions import CopyFilesAction


class FilesActionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("in setup class")

    @classmethod
    def tearDownClass(cls):
        print("in tear down class")

    def setUp(self):
        print("in setup")

    def tearDown(self):
        print("in tear down")

    def test_copy_file(self):
        print "copy file"