import unittest

from helloworld import *

class HelloWorldTest (unittest.TestCase):
    def test_round_1(self):
        assert helloworld() == "helloworld"
