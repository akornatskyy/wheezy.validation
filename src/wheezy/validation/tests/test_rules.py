""" Unit tests for ``wheezy.validation.rules``.
"""

import re
import unittest
from datetime import datetime, timedelta
from decimal import Decimal

from wheezy.validation.rules import (
    AndRule,
    Base64Rule,
    CompareRule,
    EmailRule,
    IgnoreRule,
    IntAdapterRule,
    IteratorRule,
    LengthRule,
    MissingRule,
    NotNoneRule,
    OneOfRule,
    OrRule,
    PredicateRule,
    RangeRule,
    RegexRule,
    RelativeDateDeltaRule,
    RelativeDateTimeDeltaRule,
    RelativeDeltaRule,
    RelativeTZDateDeltaRule,
    RelativeTZDateTimeDeltaRule,
    RelativeUTCDateDeltaRule,
    RelativeUTCDateTimeDeltaRule,
    RelativeUnixTimeDeltaRule,
    RequiredRule,
    ScientificRule,
    SlugRule,
    URLSafeBase64Rule,
    ValuePredicateRule,
    and_,
    base64,
    compare,
    email,
    empty,
    ignore,
    int_adapter,
    iterator,
    length,
    missing,
    model_predicate,
    must,
    not_none,
    one_of,
    or_,
    predicate,
    range,
    regex,
    relative_date,
    relative_datetime,
    relative_timestamp,
    relative_tzdate,
    relative_tzdatetime,
    relative_unixtime,
    relative_utcdate,
    relative_utcdatetime,
    required,
    required_but_missing,
    scientific,
    slug,
    standard_base64,
    urlsafe_base64,
    value_predicate,
)


class RulesTestCase(unittest.TestCase):
    def test_required(self):
        """Test `required` rule."""
        errors = []
        r = RequiredRule(message_template="required")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert not v(None)
        assert ["required"] == errors

        # Anything that python interprets as ``True`` is passing
        # this rule.
        del errors[:]
        assert v("abc")
        assert v(1)
        assert not errors

        for i in required_but_missing + [0, 0.0, ""]:
            assert not v(i)

        # shortcut
        assert isinstance(required, RequiredRule)

        r = required("customized")
        assert r != required
        assert "customized" == r.message_template

    def test_not_none(self):
        """Test `not_none` rule."""
        errors = []
        r = NotNoneRule(message_template="required")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert not v(None)
        assert ["required"] == errors

        # Anything that python interprets as ``True`` is passing
        # this rule.
        del errors[:]
        for i in (0, 0.0, "", 1, "abc"):
            assert v(i)
        assert not errors

        # shortcut
        assert isinstance(not_none, NotNoneRule)

        r = not_none("customized")
        assert r != not_none
        assert "customized" == r.message_template

    def test_missing(self):
        """Test `missing` rule."""
        errors = []
        r = MissingRule(message_template="missing")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert not v(1)
        assert ["missing"] == errors

        # Anything that python interprets as ``False`` is passing
        # this rule.
        del errors[:]
        assert v(None)
        assert v("")
        assert v(0)
        assert not errors

        for i in required_but_missing:
            assert v(i)

        # shortcut
        assert isinstance(empty, MissingRule)
        assert isinstance(missing, MissingRule)

        r = missing("customized")
        assert r != missing
        assert "customized" == r.message_template

    def test_length_strategies(self):
        """Test `length` rule strategies."""
        # shortcut
        assert length == LengthRule

        r = length(min=2)
        assert r.validate == r.check_min
        r = length(max=2)
        assert r.validate == r.check_max
        r = length()
        assert r.validate == r.succeed
        r = length(min=2, max=2)
        assert r.validate == r.check_equal
        r = length(min=1, max=2)
        assert r.validate == r.check_range

    def test_length_succeed(self):
        """Test `length` rule strategy succeed."""
        errors = []
        r = length()

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("abc")
        assert not errors

    def test_length_check_min(self):
        """Test `length` rule strategy check_min."""
        errors = []
        r = length(min=2, message_template="min %(min)d")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("ab")
        assert not errors

        assert not v("a")
        assert ["min 2"] == errors

    def test_length_check_max(self):
        """Test `length` rule strategy check_max."""
        errors = []
        r = length(max=2, message_template="max %(max)d")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("ab")
        assert not errors

        assert not v("abc")
        assert ["max 2"] == errors

    def test_length_check_equal(self):
        """Test `length` rule strategy check_equal."""
        errors = []
        r = length(min=2, max=2, message_template="len %(len)d")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("ab")
        assert not errors

        assert not v("abc")
        assert ["len 2"] == errors

    def test_length_check_range(self):
        """Test `length` rule strategy check_range."""
        errors = []
        r = length(min=2, max=3, message_template="range %(min)d-%(max)d")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("ab")
        assert not errors

        assert not v("a")
        assert ["range 2-3"] == errors

    def test_compare_strategies(self):
        """Test `compare` rule strategies."""
        # shortcut
        assert compare == CompareRule

        r = compare()
        assert r.validate == r.succeed
        r = compare(equal="confirm_password")
        assert r.validate == r.check_equal
        r = compare(not_equal="other")
        assert r.validate == r.check_not_equal

    def test_compare_succeed(self):
        """Test `compare` rule strategy succeed."""
        errors = []
        r = compare()

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("abc")

    def test_compare_check_equal(self):
        """Test `compare` rule strategy check_equal."""
        errors = []
        m = {"confirm_password": "x"}
        r = compare(equal="confirm_password")

        def v(i):
            return r.validate(i, None, m, errors, lambda s: s)

        assert v("x")
        assert not errors

        assert not v("z")
        assert errors

    def test_compare_check_not_equal(self):
        """Test `compare` rule strategy check_not_equal."""
        errors = []
        m = {"previous_password": "x"}
        r = compare(not_equal="previous_password")

        def v(i):
            return r.validate(i, None, m, errors, lambda s: s)

        assert v("z")
        assert not errors

        assert not v("x")
        assert errors

    def test_predicate(self):
        """Test `predicate` rule strategy."""
        # shortcut
        assert predicate == model_predicate == PredicateRule

        errors = []
        r = predicate(lambda m: m is not None)

        def v(i):
            return r.validate(None, None, i, errors, lambda s: s)

        assert v("x")
        assert not errors

        assert not v(None)
        assert errors

    def test_value_predicate(self):
        """Test `value_predicate` rule strategy."""
        # shortcut
        assert must == value_predicate == ValuePredicateRule

        errors = []
        r = value_predicate(lambda v: v is not None)

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v("x")
        assert not errors

        assert not v(None)
        assert errors

    def test_regex_strategies(self):
        """Test `regex` rule strategies."""
        # shortcut
        assert regex == RegexRule

        r = regex(re.compile(r"\w+"))
        assert r.validate == r.check_found
        r = regex(r"\w+", negated=False)
        assert r.validate == r.check_found
        r = regex(r"\w+", negated=True)
        assert r.validate == r.check_not_found

    def test_regex_check_found(self):
        """Test `regex` rule strategy check_found."""
        errors = []
        r = regex(r"\d+")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("1234")
        assert not errors

        assert not v("x")
        assert errors

    def test_regex_check_not_found(self):
        """Test `regex` rule strategy check_not_found."""
        errors = []
        r = regex(r"\d+", negated=True)

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("x")
        assert not errors

        assert not v("1234")
        assert errors

    def test_slug(self):
        """Test `slug` rule."""
        # shortcut
        assert isinstance(slug, SlugRule)

        errors = []
        r = slug

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v("x14")
        assert not errors

        assert not v("x%")
        assert errors

        r = slug(message_template="customized")
        assert r != slug
        assert "customized" == r.message_template

    def test_email(self):
        """Test `email` rule."""
        # shortcut
        assert isinstance(email, EmailRule)

        errors = []
        r = email

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v("x.14@somewhere.org")
        assert not errors

        assert not v("x.14@somewhere.or g")
        assert errors

        r = email(message_template="customized")
        assert r != email
        assert "customized" == r.message_template

    def test_scientific(self):
        """Test `scientific` rule."""
        # shortcut
        assert isinstance(scientific, ScientificRule)

        errors = []
        r = scientific

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v("12.5e-3")
        assert not errors

        assert not v("12.x")
        assert errors

        r = scientific(message_template="customized")
        assert r != scientific
        assert "customized" == r.message_template

    def test_base64(self):
        """Test `base64` rule."""
        # shortcut
        assert isinstance(base64, Base64Rule)

        errors = []
        r = base64

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v("d2hlZXp5")
        assert v("d2hlZXp51+==")
        assert v("d2hlZXp51/==")
        assert v("d2hlZXp51+/=")
        assert not errors

        assert not v("dx-_")
        assert errors

        # shortcut
        assert isinstance(base64, Base64Rule)
        assert isinstance(standard_base64, Base64Rule)

        r = base64(message_template="customized")
        assert r != base64
        assert "customized" == r.message_template

    def test_base64alt(self):
        """Test `base64` rule."""
        errors = []
        r = Base64Rule(altchars="-_")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v("d2hlZXp5")
        assert v("d2hlZXp51-==")
        assert v("d2hlZXp51_==")
        assert v("d2hlZXp51-_=")
        assert not errors

        assert not v("dx+/")
        assert errors

    def test_urlsafe_base64(self):
        """Test `urlsafe_base64` rule."""
        # shortcut
        assert isinstance(urlsafe_base64, URLSafeBase64Rule)

        errors = []
        r = urlsafe_base64

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v("d2hlZXp5")
        assert v("d2hlZXp51-==")
        assert v("d2hlZXp51_==")
        assert v("d2hlZXp51-_=")
        assert not errors

        assert not v("dx+/")
        assert errors

        r = urlsafe_base64(message_template="customized")
        assert r != urlsafe_base64
        assert "customized" == r.message_template

    def test_range_strategies(self):
        """Test `range` rule strategies."""
        # shortcut
        assert range == RangeRule

        r = range()
        assert r.validate == r.succeed
        r = range(min=0)
        assert r.validate == r.check_min
        r = range(min=2)
        assert r.validate == r.check_min
        r = range(max=0)
        assert r.validate == r.check_max
        r = range(max=2)
        assert r.validate == r.check_max
        r = range(min=0, max=0)
        assert r.validate == r.check_range
        r = range(min=2, max=2)
        assert r.validate == r.check_range

        r = range(min=Decimal(0))
        assert r.validate == r.check_min

        errors = []
        r = range(max=Decimal("15"))

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(Decimal("10"))
        assert not errors

        assert not v(Decimal("20"))
        assert errors

    def test_range_succeed(self):
        """Test `range` rule strategy succeed."""
        errors = []
        r = range()

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(100)

    def test_range_check_min(self):
        """Test `range` rule strategy check_min."""
        errors = []
        r = range(min=10, message_template="min %(min)s")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(10)
        assert not errors

        assert not v(1)
        assert ["min 10"] == errors

    def test_range_check_max(self):
        """Test `range` rule strategy check_max."""
        errors = []
        r = range(max=10, message_template="max %(max)s")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(10)
        assert not errors

        assert not v(11)
        assert ["max 10"] == errors

    def test_range_check_range(self):
        """Test `range` rule strategy check_range."""
        errors = []
        r = range(min=2, max=3, message_template="range %(min)s-%(max)s")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(2)
        assert not errors

        assert not v(1)
        assert ["range 2-3"] == errors

    def test_and(self):
        """Test `and` rule."""
        # shortcut
        assert and_ == AndRule

        errors = []
        r = and_(required, range(min=1, max=5))

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(1)
        assert not errors

        assert not v(0)
        assert 1 == len(errors)

        self.assertRaises(AssertionError, lambda: and_())
        self.assertRaises(AssertionError, lambda: and_(required))

    def test_or(self):
        """Test `or` rule."""
        # shortcut
        assert or_ == OrRule

        errors = []
        r = or_(range(min=1, max=5), range(min=11, max=15))

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(1)
        assert v(12)
        assert not errors

        assert not v(0)
        assert 2 == len(errors)

        self.assertRaises(AssertionError, lambda: or_())
        self.assertRaises(AssertionError, lambda: or_(range()))

    def test_iterator(self):
        """Test `iterator` rule."""
        # shortcut
        assert iterator == IteratorRule

        errors = []
        r = iterator(rules=[required, range(min=1, max=5)])

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v([1, 2, 3])
        assert not errors

        assert not v([1, 7, 9])
        assert 1 == len(errors)

        r.stop = False
        del errors[:]
        assert not v([1, 7, 9])
        assert 2 == len(errors)

        self.assertRaises(AssertionError, lambda: iterator([]))

    def test_one_of(self):
        """Test `one_of` rule."""
        # shortcut
        assert one_of == OneOfRule

        errors = []
        r = one_of([1, 2, 3, None])

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(3)
        assert not errors

        assert not v(7)
        assert errors

        self.assertRaises(AssertionError, lambda: one_of([]))

    def test_relative_rule(self):
        """Test `RelativeDeltaRule` now raises error."""
        r = RelativeDeltaRule()
        self.assertRaises(NotImplementedError, r.now)

    def test_ignore(self):
        """Test `ignore` rule."""
        # shortcut
        assert ignore == IgnoreRule

        errors = []
        r = ignore(1, a=2, b="anything")

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(100)
        assert v("x")
        assert not errors

    def test_adapter(self):
        """Test `adapter` and `int_adapter` rules."""
        # shortcut
        assert int_adapter == IntAdapterRule

        errors = []
        r = int_adapter(range(min=1))

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("100")
        assert v("1")
        assert not errors

        assert not v("0")
        assert errors
        del errors[:]
        assert not v("X")
        assert errors


class RelativeDeltaRuleMixin(object):
    def test_shortcut(self):
        """Test rule shortcut."""
        assert self.shortcut == self.Rule

    def test_strategies(self):
        """Test rule strategies."""
        r = self.shortcut()
        assert r.validate == r.succeed
        r = self.shortcut(min=2)
        assert r.validate == r.check_min
        r = self.shortcut(max=2)
        assert r.validate == r.check_max
        r = self.shortcut(min=2, max=2)
        assert r.validate == r.check_range

    def test_succeed(self):
        """Test succeed strategy."""
        errors = []
        r = self.shortcut()

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(r.now())

    def test_check_min(self):
        """Test check_min strategy."""
        errors = []
        r = self.shortcut(min=timedelta(days=-7))

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(r.now())
        assert not errors

        assert not v(r.now() - timedelta(days=8))
        assert errors

    def test_check_max(self):
        """Test check_max strategy."""
        errors = []
        r = self.shortcut(max=timedelta(days=7))

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(r.now())
        assert not errors

        assert not v(r.now() + timedelta(days=8))
        assert errors

    def test_check_range(self):
        """Test check_range strategy."""
        errors = []
        r = self.shortcut(min=timedelta(days=-7), max=timedelta(days=7))

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(r.now())
        assert not errors

        assert not v(r.now() - timedelta(days=8))
        assert errors

        del errors[:]
        assert not v(r.now() + timedelta(days=8))
        assert errors


class RelativeDateDeltaRuleTestCase(unittest.TestCase, RelativeDeltaRuleMixin):
    def setUp(self):
        self.shortcut = relative_date
        self.Rule = RelativeDateDeltaRule


class RelativeUTCDateDeltaRuleTestCase(
    unittest.TestCase, RelativeDeltaRuleMixin
):
    def setUp(self):
        self.shortcut = relative_utcdate
        self.Rule = RelativeUTCDateDeltaRule


class RelativeTZDateDeltaRuleTestCase(
    unittest.TestCase, RelativeDeltaRuleMixin
):
    def setUp(self):
        self.shortcut = relative_tzdate
        self.Rule = RelativeTZDateDeltaRule


class RelativeDateTimeDeltaRuleTestCase(
    unittest.TestCase, RelativeDeltaRuleMixin
):
    def setUp(self):
        self.shortcut = relative_datetime
        self.Rule = RelativeDateTimeDeltaRule


class RelativeUTCDateTimeDeltaRuleTestCase(
    unittest.TestCase, RelativeDeltaRuleMixin
):
    def setUp(self):
        self.shortcut = relative_utcdatetime
        self.Rule = RelativeUTCDateTimeDeltaRule


class RelativeTZDateTimeDeltaRuleTestCase(
    unittest.TestCase, RelativeDeltaRuleMixin
):
    def setUp(self):
        self.shortcut = relative_tzdatetime
        self.Rule = RelativeTZDateTimeDeltaRule


class RelativeUnixTimeDeltaRuleTestCase(
    unittest.TestCase, RelativeDeltaRuleMixin
):
    def setUp(self):
        class Proxy(RelativeUnixTimeDeltaRule):
            def now(self):
                t = super(Proxy, self).now()
                return datetime.fromtimestamp(t)

        self.shortcut = Proxy
        self.Rule = RelativeUnixTimeDeltaRule

    def test_shortcut(self):
        """Test rule shortcut."""
        assert relative_unixtime == RelativeUnixTimeDeltaRule
        assert relative_unixtime == relative_timestamp
