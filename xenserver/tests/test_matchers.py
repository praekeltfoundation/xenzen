from testtools.assertions import assert_that
from testtools.matchers import Is, Not

from xenserver.tests.matchers import ExtractValue


class TestExtractValue(object):

    def test_extraction(self):
        """
        An ExtractValue instance will extract whatever value it is first
        compared to and will pass the match.
        """
        ev = ExtractValue("a")
        assert not ev.matched
        assert ev.value is None
        assert_that(7, ev)
        assert ev.matched
        assert ev.value == 7

        ev = ExtractValue("b")
        assert not ev.matched
        assert ev.value is None
        assert_that("hello", ev)
        assert ev.matched
        assert ev.value == "hello"

    def test_matching(self):
        """
        An ExtractValue instance that already has a value v will match as if it
        were Equals(v).
        """
        ev = ExtractValue("a")
        assert_that(7, ev)
        assert_that(8, Not(ev))
        assert_that(7, ev)
        assert_that(ev.match(7), Is(None))
        assert_that(ev.match(19), Not(Is(None)))

        ev = ExtractValue("b")
        assert_that("hello", ev)
        assert_that(7, Not(ev))
        assert_that("hello", ev)
        assert_that(ev.match("hello"), Is(None))
        assert_that(ev.match("bye"), Not(Is(None)))

    def test_str(self):
        """
        ExtractValue instances stringify sensibly.
        """
        ev = ExtractValue("a")
        assert str(ev) == "ExtractValue(a)"
        assert_that(3, ev)
        assert str(ev) == "ExtractValue(a)=[3]"
