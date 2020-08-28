""" Unit tests for ``wheezy.validation.rules``.
"""

import unittest


class RulesTestCase(unittest.TestCase):
    def test_required(self):
        """Test `required` rule."""
        from wheezy.validation.rules import (
            RequiredRule,
            required,
            required_but_missing,
        )

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
        from wheezy.validation.rules import NotNoneRule, not_none

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
        from wheezy.validation.rules import (
            MissingRule,
            empty,
            missing,
            required_but_missing,
        )

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
        from wheezy.validation.rules import LengthRule, length

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
        from wheezy.validation.rules import length

        errors = []
        r = length()

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("abc")
        assert not errors

    def test_length_check_min(self):
        """Test `length` rule strategy check_min."""
        from wheezy.validation.rules import length

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
        from wheezy.validation.rules import length

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
        from wheezy.validation.rules import length

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
        from wheezy.validation.rules import length

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
        from wheezy.validation.rules import CompareRule, compare

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
        from wheezy.validation.rules import compare

        errors = []
        r = compare()

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v("abc")

    def test_compare_check_equal(self):
        """Test `compare` rule strategy check_equal."""
        from wheezy.validation.rules import compare

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
        from wheezy.validation.rules import compare

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
        from wheezy.validation.rules import (
            PredicateRule,
            model_predicate,
            predicate,
        )

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
        from wheezy.validation.rules import (
            ValuePredicateRule,
            must,
            value_predicate,
        )

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
        import re

        from wheezy.validation.rules import RegexRule, regex

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
        from wheezy.validation.rules import regex

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
        from wheezy.validation.rules import regex

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
        from wheezy.validation.rules import SlugRule, slug

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
        from wheezy.validation.rules import EmailRule, email

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
        from wheezy.validation.rules import ScientificRule, scientific

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
        from wheezy.validation.rules import Base64Rule, base64, standard_base64

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
        from wheezy.validation.rules import Base64Rule

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
        from wheezy.validation.rules import URLSafeBase64Rule, urlsafe_base64

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
        from wheezy.validation.rules import RangeRule, range

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

        from wheezy.validation.comp import Decimal

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
        from wheezy.validation.rules import range

        errors = []
        r = range()

        def v(i):
            return r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(100)

    def test_range_check_min(self):
        """Test `range` rule strategy check_min."""
        from wheezy.validation.rules import range

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
        from wheezy.validation.rules import range

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
        from wheezy.validation.rules import range

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
        from wheezy.validation.rules import AndRule, and_, range, required

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
        from wheezy.validation.rules import OrRule, or_, range

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
        from wheezy.validation.rules import (
            IteratorRule,
            iterator,
            range,
            required,
        )

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
        from wheezy.validation.rules import OneOfRule, one_of

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
        from wheezy.validation.rules import RelativeDeltaRule

        r = RelativeDeltaRule()
        self.assertRaises(NotImplementedError, r.now)

    def test_ignore(self):
        """Test `ignore` rule."""
        from wheezy.validation.rules import IgnoreRule, ignore

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
        from wheezy.validation.rules import IntAdapterRule, int_adapter, range

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
        from datetime import timedelta

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
        from datetime import timedelta

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
        from datetime import timedelta

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


class RelativeDateDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):
    def setUp(self):
        from wheezy.validation.rules import (
            RelativeDateDeltaRule,
            relative_date,
        )

        self.shortcut = relative_date
        self.Rule = RelativeDateDeltaRule


class RelativeUTCDateDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):
    def setUp(self):
        from wheezy.validation.rules import (
            RelativeUTCDateDeltaRule,
            relative_utcdate,
        )

        self.shortcut = relative_utcdate
        self.Rule = RelativeUTCDateDeltaRule


class RelativeTZDateDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):
    def setUp(self):
        from wheezy.validation.rules import (
            RelativeTZDateDeltaRule,
            relative_tzdate,
        )

        self.shortcut = relative_tzdate
        self.Rule = RelativeTZDateDeltaRule


class RelativeDateTimeDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):
    def setUp(self):
        from wheezy.validation.rules import (
            RelativeDateTimeDeltaRule,
            relative_datetime,
        )

        self.shortcut = relative_datetime
        self.Rule = RelativeDateTimeDeltaRule


class RelativeUTCDateTimeDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):
    def setUp(self):
        from wheezy.validation.rules import (
            RelativeUTCDateTimeDeltaRule,
            relative_utcdatetime,
        )

        self.shortcut = relative_utcdatetime
        self.Rule = RelativeUTCDateTimeDeltaRule


class RelativeTZDateTimeDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):
    def setUp(self):
        from wheezy.validation.rules import (
            RelativeTZDateTimeDeltaRule,
            relative_tzdatetime,
        )

        self.shortcut = relative_tzdatetime
        self.Rule = RelativeTZDateTimeDeltaRule


class RelativeUnixTimeDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):
    def setUp(self):
        from datetime import datetime

        from wheezy.validation.rules import RelativeUnixTimeDeltaRule

        class Proxy(RelativeUnixTimeDeltaRule):
            def now(self):
                t = super(Proxy, self).now()
                return datetime.fromtimestamp(t)

        self.shortcut = Proxy
        self.Rule = RelativeUnixTimeDeltaRule

    def test_shortcut(self):
        """Test rule shortcut."""
        from wheezy.validation.rules import (
            RelativeUnixTimeDeltaRule,
            relative_timestamp,
            relative_unixtime,
        )

        assert relative_unixtime == RelativeUnixTimeDeltaRule
        assert relative_unixtime == relative_timestamp
