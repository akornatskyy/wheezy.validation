
""" Unit tests for ``wheezy.validation.rules``.
"""

import unittest


class RulesTestCase(unittest.TestCase):

    def test_required(self):
        """ Test `required` rule.
        """
        from wheezy.validation.rules import RequiredRule
        from wheezy.validation.rules import required
        from wheezy.validation.rules import required_but_missing

        errors = []
        r = RequiredRule(message_template='required')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert not v(None)
        assert ['required'] == errors

        # Anything that python interprets as ``True`` is passing
        # this rule.
        del errors[:]
        assert v('abc')
        assert v(1)
        assert not errors

        for i in required_but_missing:
            assert not v(i)

        # shortcut
        assert isinstance(required, RequiredRule)

        r = required('customized')
        assert r != required
        assert 'customized' == r.message_template

    def test_missing(self):
        """ Test `missing` rule.
        """
        from wheezy.validation.rules import MissingRule
        from wheezy.validation.rules import missing
        from wheezy.validation.rules import required_but_missing

        errors = []
        r = MissingRule(message_template='missing')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert not v(1)
        assert ['missing'] == errors

        # Anything that python interprets as ``False`` is passing
        # this rule.
        del errors[:]
        assert v(None)
        assert v('')
        assert v(0)
        assert not errors

        for i in required_but_missing:
            assert v(i)

        # shortcut
        assert isinstance(missing, MissingRule)

        r = missing('customized')
        assert r != missing
        assert 'customized' == r.message_template

    def test_length_strategies(self):
        """ Test `length` rule strategies.
        """
        from wheezy.validation.rules import LengthRule
        from wheezy.validation.rules import length

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
        """ Test `length` rule strategy succeed.
        """
        from wheezy.validation.rules import length

        errors = []
        r = length()
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v('abc')
        assert not errors

    def test_length_check_min(self):
        """ Test `length` rule strategy check_min.
        """
        from wheezy.validation.rules import length

        errors = []
        r = length(min=2, message_template='min %(min)d')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v('ab')
        assert not errors

        assert not v('a')
        assert ['min 2'] == errors

    def test_length_check_max(self):
        """ Test `length` rule strategy check_max.
        """
        from wheezy.validation.rules import length

        errors = []
        r = length(max=2, message_template='max %(max)d')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v('ab')
        assert not errors

        assert not v('abc')
        assert ['max 2'] == errors

    def test_length_check_equal(self):
        """ Test `length` rule strategy check_equal.
        """
        from wheezy.validation.rules import length

        errors = []
        r = length(min=2, max=2, message_template='len %(len)d')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v('ab')
        assert not errors

        assert not v('abc')
        assert ['len 2'] == errors

    def test_length_check_range(self):
        """ Test `length` rule strategy check_range.
        """
        from wheezy.validation.rules import length

        errors = []
        r = length(min=2, max=3, message_template='range %(min)d-%(max)d')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v('ab')
        assert not errors

        assert not v('a')
        assert ['range 2-3'] == errors

    def test_compare_strategies(self):
        """ Test `compare` rule strategies.
        """
        from wheezy.validation.rules import CompareRule
        from wheezy.validation.rules import compare

        # shortcut
        assert compare == CompareRule

        r = compare()
        assert r.validate == r.succeed
        r = compare(equal='confirm_password')
        assert r.validate == r.check_equal
        r = compare(not_equal='other')
        assert r.validate == r.check_not_equal

    def test_compare_succeed(self):
        """ Test `compare` rule strategy succeed.
        """
        from wheezy.validation.rules import compare

        errors = []
        r = compare()
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v('abc')

    def test_compare_check_equal(self):
        """ Test `compare` rule strategy check_equal.
        """
        from wheezy.validation.rules import compare

        errors = []
        m = {'confirm_password': 'x'}
        r = compare(equal='confirm_password')
        v = lambda i: r.validate(i, None, m, errors, lambda s: s)

        assert v('x')
        assert not errors

        assert not v('z')
        assert errors

    def test_compare_check_not_equal(self):
        """ Test `compare` rule strategy check_not_equal.
        """
        from wheezy.validation.rules import compare

        errors = []
        m = {'previous_password': 'x'}
        r = compare(not_equal='previous_password')
        v = lambda i: r.validate(i, None, m, errors, lambda s: s)

        assert v('z')
        assert not errors

        assert not v('x')
        assert errors

    def test_predicate(self):
        """ Test `predicate` rule strategy.
        """
        from wheezy.validation.rules import PredicateRule
        from wheezy.validation.rules import predicate

        # shortcut
        assert predicate == PredicateRule

        errors = []
        r = predicate(lambda m: m is not None)
        v = lambda i: r.validate(None, None, i, errors, lambda s: s)

        assert v('x')
        assert not errors

        assert not v(None)
        assert errors

    def test_regex_strategies(self):
        """ Test `regex` rule strategies.
        """
        import re
        from wheezy.validation.rules import RegexRule
        from wheezy.validation.rules import regex

        # shortcut
        assert regex == RegexRule

        r = regex(re.compile(r'\w+'))
        assert r.validate == r.check_found
        r = regex(r'\w+', negated=False)
        assert r.validate == r.check_found
        r = regex(r'\w+', negated=True)
        assert r.validate == r.check_not_found

    def test_regex_check_found(self):
        """ Test `regex` rule strategy check_found.
        """
        from wheezy.validation.rules import regex

        errors = []
        r = regex(r'\d+')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v('1234')
        assert not errors

        assert not v('x')
        assert errors

    def test_regex_check_not_found(self):
        """ Test `regex` rule strategy check_not_found.
        """
        from wheezy.validation.rules import regex

        errors = []
        r = regex(r'\d+', negated=True)
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v('x')
        assert not errors

        assert not v('1234')
        assert errors

    def test_slug(self):
        """ Test `slug` rule.
        """
        from wheezy.validation.rules import SlugRule
        from wheezy.validation.rules import slug

        # shortcut
        assert isinstance(slug, SlugRule)

        errors = []
        r = slug
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v('x14')
        assert not errors

        assert not v('x%')
        assert errors

        r = slug(message_template='customized')
        assert r != slug
        assert 'customized' == r.message_template

    def test_email(self):
        """ Test `email` rule.
        """
        from wheezy.validation.rules import EmailRule
        from wheezy.validation.rules import email

        # shortcut
        assert isinstance(email, EmailRule)

        errors = []
        r = email
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v('x.14@somewhere.org')
        assert not errors

        assert not v('x.14@somewhere.or g')
        assert errors

        r = email(message_template='customized')
        assert r != email
        assert 'customized' == r.message_template

    def test_range_strategies(self):
        """ Test `range` rule strategies.
        """
        from wheezy.validation.rules import RangeRule
        from wheezy.validation.rules import range

        # shortcut
        assert range == RangeRule

        r = range()
        assert r.validate == r.succeed
        r = range(min=2)
        assert r.validate == r.check_min
        r = range(max=2)
        assert r.validate == r.check_max
        r = range(min=2, max=2)
        assert r.validate == r.check_range

        from wheezy.validation.comp import Decimal

        errors = []
        r = range(max=Decimal('15'))
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(Decimal('10'))
        assert not errors

        assert not v(Decimal('20'))
        assert errors

    def test_range_succeed(self):
        """ Test `range` rule strategy succeed.
        """
        from wheezy.validation.rules import range

        errors = []
        r = range()
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(100)

    def test_range_check_min(self):
        """ Test `range` rule strategy check_min.
        """
        from wheezy.validation.rules import range

        errors = []
        r = range(min=10, message_template='min %(min)s')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(10)
        assert not errors

        assert not v(1)
        assert ['min 10'] == errors

    def test_range_check_max(self):
        """ Test `range` rule strategy check_max.
        """
        from wheezy.validation.rules import range

        errors = []
        r = range(max=10, message_template='max %(max)s')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(10)
        assert not errors

        assert not v(11)
        assert ['max 10'] == errors

    def test_range_check_range(self):
        """ Test `range` rule strategy check_range.
        """
        from wheezy.validation.rules import range

        errors = []
        r = range(min=2, max=3, message_template='range %(min)s-%(max)s')
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(2)
        assert not errors

        assert not v(1)
        assert ['range 2-3'] == errors

    def test_and(self):
        """ Test `and` rule.
        """
        from wheezy.validation.rules import AndRule
        from wheezy.validation.rules import and_
        from wheezy.validation.rules import required
        from wheezy.validation.rules import range

        # shortcut
        assert and_ == AndRule

        errors = []
        r = and_(required, range(min=1, max=5))
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(1)
        assert not errors

        assert not v(0)
        assert 2 == len(errors)

        self.assertRaises(AssertionError, lambda: and_())
        self.assertRaises(AssertionError, lambda: and_(required))

    def test_or(self):
        """ Test `or` rule.
        """
        from wheezy.validation.rules import OrRule
        from wheezy.validation.rules import or_
        from wheezy.validation.rules import range

        # shortcut
        assert or_ == OrRule

        errors = []
        r = or_(range(min=1, max=5), range(min=11, max=15))
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(1)
        assert v(12)
        assert not errors

        assert not v(0)
        assert 2 == len(errors)

        self.assertRaises(AssertionError, lambda: or_())
        self.assertRaises(AssertionError, lambda: or_(range()))

    def test_iterator(self):
        """ Test `iterator` rule.
        """
        from wheezy.validation.rules import IteratorRule
        from wheezy.validation.rules import iterator
        from wheezy.validation.rules import required
        from wheezy.validation.rules import range

        # shortcut
        assert iterator == IteratorRule

        errors = []
        r = iterator(rules=[required, range(min=1, max=5)])
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

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
        """ Test `one_of` rule.
        """
        from wheezy.validation.rules import OneOfRule
        from wheezy.validation.rules import one_of

        # shortcut
        assert one_of == OneOfRule

        errors = []
        r = one_of([1, 2, 3, None])
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(3)
        assert not errors

        assert not v(7)
        assert errors

        self.assertRaises(AssertionError, lambda: one_of([]))


class RelativeDeltaRuleMixin:

    def test_strategies(self):
        """ Test rule strategies.
        """
        # shortcut
        assert self.shortcut == self.Rule

        r = self.shortcut()
        assert r.validate == r.succeed
        r = self.shortcut(min=2)
        assert r.validate == r.check_min
        r = self.shortcut(max=2)
        assert r.validate == r.check_max
        r = self.shortcut(min=2, max=2)
        assert r.validate == r.check_range

    def test_succeed(self):
        """ Test succeed strategy.
        """
        errors = []
        r = self.shortcut()
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(None)
        assert v(r.now())

    def test_check_min(self):
        """ Test check_min strategy.
        """
        from datetime import timedelta
        errors = []
        r = self.shortcut(min=timedelta(days=-7))
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(r.now())
        assert not errors

        assert not v(r.now() - timedelta(days=8))
        assert errors

    def test_check_max(self):
        """ Test check_max strategy.
        """
        from datetime import timedelta
        errors = []
        r = self.shortcut(max=timedelta(days=7))
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(r.now())
        assert not errors

        assert not v(r.now() + timedelta(days=8))
        assert errors

    def test_check_range(self):
        """ Test check_range strategy.
        """
        from datetime import timedelta
        errors = []
        r = self.shortcut(min=timedelta(days=-7), max=timedelta(days=7))
        v = lambda i: r.validate(i, None, None, errors, lambda s: s)

        assert v(r.now())
        assert not errors

        assert not v(r.now() - timedelta(days=8))
        assert errors

        del errors[:]
        assert not v(r.now() + timedelta(days=8))
        assert errors


class RelativeDateDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):

    def setUp(self):
        from wheezy.validation.rules import RelativeDateDeltaRule
        from wheezy.validation.rules import relative_date
        self.shortcut = relative_date
        self.Rule = RelativeDateDeltaRule


class RelativeDateTimeDeltaRule(unittest.TestCase, RelativeDeltaRuleMixin):

    def setUp(self):
        from wheezy.validation.rules import RelativeDateTimeDeltaRule
        from wheezy.validation.rules import relative_datetime
        self.shortcut = relative_datetime
        self.Rule = RelativeDateTimeDeltaRule
