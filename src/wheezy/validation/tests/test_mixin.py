
""" Unit tests for ``wheezy.validation.mixin``.
"""

import unittest

from wheezy.validation.mixin import ValidationMixin


class MyService(ValidationMixin):

    def __init__(self):
        self.errors = {}
        self.translations = {'validation': None}


class ValidationMixinTestCase(unittest.TestCase):

    def test_errors(self):
        """ Ensure error summary.
        """
        s = MyService()
        s.error('error-message-1')
        assert {'__ERROR__': ['error-message-1']} == s.errors

        s.error('error-message-2')
        assert [('__ERROR__', [
            'error-message-1',
            'error-message-2'])] == sorted(s.errors.items())

    def test_validate(self):
        """
        """
        from wheezy.validation.rules import required
        from wheezy.validation.validator import Validator
        v = Validator({
            'name': [required]
        })
        user = {'name': 'john'}
        s = MyService()
        assert s.validate(user, v)
        assert not s.errors

        user = {'name': None}
        assert not s.validate(user, v)
        assert s.errors['name']
