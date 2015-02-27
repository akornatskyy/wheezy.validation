
""" Unit tests for ``wheezy.validation.model``.
"""

import unittest

from datetime import date
from datetime import datetime
from datetime import time

from wheezy.validation.comp import Decimal


class User(object):
    name = ''
    age = 0
    balance = Decimal(0)
    birthday = date.min
    lunch_time = time.min
    last_visit = datetime.min
    accepted_policy = False

    def __init__(self):
        self.prefs = []
        self.prefs2 = [0]


class TryUpdateModelTestCase(unittest.TestCase):

    def setUp(self):
        self.values = {
            'name': 'john', 'balance': ['0.1'],
            'age': ['33'], 'birthday': ['1978/4/9'],
            'lunch_time': ['13:05'], 'last_visit': ['2012/2/4 16:14:52'],
            'accepted_policy': ['1'], 'prefs': ['1', '2'],
            'prefs2': ['1', '2']
        }

    def test_update_class_instance(self):
        """ Ensure try_update_model works with python class instance.
        """
        from wheezy.validation.model import try_update_model

        errors = {}
        user = User()

        assert try_update_model(user, self.values, errors)
        assert not errors

        assert 'john' == user.name

        assert Decimal('0.1') == user.balance
        assert 33 == user.age

        assert date(1978, 4, 9) == user.birthday
        assert time(13, 5) == user.lunch_time
        assert datetime(2012, 2, 4, 16, 14, 52) == user.last_visit
        assert user.accepted_policy

        assert ['1', '2'] == user.prefs
        assert [1, 2] == user.prefs2

    def test_update_dict(self):
        """ Ensure try_update_model works with dict python object.
        """
        from wheezy.validation.model import try_update_model

        errors = {}
        user = {'name': '', 'age': '0', 'extra': ''}

        assert try_update_model(user, self.values, errors)
        assert not errors

        assert 'john' == user['name']
        assert '33' == user['age']

    def test_invalid_input(self):
        """ Ensure errors and preserved original value for invalid input.
        """
        from wheezy.validation.model import try_update_model
        self.values.update({
            'balance': ['x'],
            'age': ['x'],
            'birthday': ['4.2.12'],
            'prefs2': ['1', 'x']
        })

        errors = {}
        user = User()

        assert not try_update_model(user, self.values, errors)
        assert errors
        assert errors['balance']
        assert errors['age']
        assert errors['birthday']
        assert errors['prefs2']
        assert Decimal(0) == user.balance
        assert 0 == user.age
        assert date.min == user.birthday
        assert [0] == user.prefs2


class ValueProviderTestCase(unittest.TestCase):

    def test_int_value_provider(self):
        """ Ensure `int_value_provider` is parsing input correctly.
        """
        from wheezy.validation.model import int_value_provider

        def vp(s):
            return int_value_provider(s, lambda x: x)

        assert 100 == vp('100')
        assert 1000 == vp('1000')
        assert 1000 == vp('1,000')
        assert 1000000 == vp('1,000,000')

        # An empty string value is converted to None
        assert vp('') is None
        assert vp('  ') is None

    def test_decimal_value_provider(self):
        """ Ensure `decimal_value_provider` is parsing input correctly.
        """
        from wheezy.validation.model import decimal_value_provider

        def vp(s):
            return decimal_value_provider(s, lambda x: x)

        assert Decimal('100') == vp('100')
        assert Decimal('100.0') == vp('100.0')
        assert Decimal('1000') == vp('1000')
        assert Decimal('1000') == vp('1,000')
        assert Decimal('1000000') == vp('1,000,000')
        assert Decimal('1007.85') == vp('1,007.85')
        assert Decimal('0') == vp('0')
        assert Decimal('0') == vp('0.0')
        assert Decimal('0') == vp('0.00')

        # An empty string value is converted to None
        assert vp('') is None
        assert vp('  ') is None

    def test_bool_value_provider(self):
        """ Ensure `bool_value_provider` is parsing input correctly.
        """
        from wheezy.validation.model import bool_value_provider
        from wheezy.validation.model import boolean_true_values

        def vp(s):
            return bool_value_provider(s, lambda x: x)

        for s in boolean_true_values:
            assert vp(s)
        assert not vp('0')

        # An empty string value is converted to False.
        assert not vp('')
        assert not vp('  ')

    def test_float_value_provider(self):
        """ Ensure `float_value_provider` is parsing input correctly.
        """
        from wheezy.validation.model import float_value_provider

        def vp(s):
            return float_value_provider(s, lambda x: x)

        assert 1.0 == vp('1.00')
        assert 1.5 == vp('1.5')
        assert 4531.5 == vp('4,531.5')

        # An empty string value is converted to None.
        assert vp('') is None
        assert vp('  ') is None

    def test_date_value_provider(self):
        """ Ensure `date_value_provider` is parsing input correctly.
        """
        from wheezy.validation.model import date_value_provider

        def vp(s):
            return date_value_provider(s, lambda x: x)

        assert date(2012, 2, 4) == vp(' 2012/2/4')
        assert date(2012, 2, 4) == vp('2/4/2012 ')
        assert date(2012, 2, 4) == vp('2012-2-4')
        assert date(2012, 2, 4) == vp('2/4/12')

        # An empty string value is converted to None.
        assert vp('') is None
        assert vp('  ') is None

        # If none of known formats match raise ValueError.
        self.assertRaises(ValueError, lambda: vp('2.4.12'))

    def test_time_value_provider(self):
        """ Ensure `time_value_provider` is parsing input correctly.
        """
        from wheezy.validation.model import time_value_provider

        def vp(s):
            return time_value_provider(s, lambda x: x)

        assert time(15, 40) == vp(' 15:40')
        assert time(15, 40, 11) == vp('15:40:11 ')

        # An empty string value is converted to None.
        assert vp('') is None
        assert vp('  ') is None

        # If none of known formats match raise ValueError.
        self.assertRaises(ValueError, lambda: vp('2.45.17'))

    def test_datetime_value_provider(self):
        """ Ensure `datetime_value_provider` is parsing input correctly.
        """
        from wheezy.validation.model import datetime_value_provider

        def vp(s):
            return datetime_value_provider(s, lambda x: x)

        assert datetime(2008, 5, 18, 15, 40) == vp('2008/5/18 15:40')

        # If none of known formats match try date_value_provider.

        assert datetime(2008, 5, 18, 0, 0) == vp('2008/5/18')

        # An empty string value is converted to None.
        assert vp('') is None
        assert vp('  ') is None

        # If none of known formats match raise ValueError.
        self.assertRaises(ValueError, lambda: vp('2.4.12'))
