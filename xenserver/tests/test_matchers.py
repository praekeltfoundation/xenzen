from unittest import TestCase

from xenserver.tests.matchers import NO_VALUE, ANY_VALUE, ExtractValue


class TestXenServerHelpers(TestCase):

    def test_NO_VALUE_identity(self):
        """
        NO_VALUE is NO_VALUE
        """
        assert NO_VALUE is NO_VALUE
        assert NO_VALUE is not 3

    def test_NO_VALUE_equality(self):
        """
        NO_VALUE is equal to nothing
        """
        assert NO_VALUE != NO_VALUE
        assert NO_VALUE != 1
        assert NO_VALUE != "hello"

    def test_NO_VALUE_repr(self):
        """
        NO_VALUE stringifies sensibly.
        """
        assert str(NO_VALUE) == "<NO VALUE>"
        assert repr(NO_VALUE) == "<NO VALUE>"

    def test_ANY_VALUE_identity(self):
        """
        ANY_VALUE is ANY_VALUE
        """
        assert ANY_VALUE is ANY_VALUE
        assert ANY_VALUE is not 3

    def test_ANY_VALUE_equality(self):
        """
        ANY_VALUE is equal to everything
        """
        assert ANY_VALUE == ANY_VALUE
        assert ANY_VALUE == 1
        assert ANY_VALUE == "hello"

    def test_ANY_VALUE_repr(self):
        """
        ANY_VALUE stringifies sensibly.
        """
        assert str(ANY_VALUE) == "<ANY VALUE>"
        assert repr(ANY_VALUE) == "<ANY VALUE>"

    def test_ExtractValue_extraction(self):
        """
        An ExtractValue instance will extract whatever value it is first
        compared to and return True for the comparison.
        """
        ev = ExtractValue("a")
        assert ev.value is NO_VALUE
        assert ev == 7
        assert ev.value == 7

        ev = ExtractValue("b")
        assert ev.value is NO_VALUE
        assert ev == "hello"
        assert ev.value == "hello"

    def test_ExtractValue_equality(self):
        """
        An ExtractValue instance that already has a value will compare as if it
        were that value.
        """
        ev = ExtractValue("a")
        assert ev == 7
        assert ev != 8
        assert ev == 7

        ev = ExtractValue("b")
        assert ev == "hello"
        assert ev != 7
        assert ev == "hello"
        assert ev != "bye"

    def test_ExtractValue_repr(self):
        """
        ExtractValue instances stringify sensibly.
        """
        ev = ExtractValue("a")
        assert str(ev) == "<ExtractValue a=<NO VALUE>>"
        assert repr(ev) == "<ExtractValue a=<NO VALUE>>"
        ev == 3
        assert str(ev) == "<ExtractValue a=3>"
        assert repr(ev) == "<ExtractValue a=3>"
