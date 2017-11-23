from unittest import TestCase


def something():
    return 'something'


class TestSomething(TestCase):
    def test_is_string(self):
        s = something()
        self.assertEqual(s, 'something')
