import unittest

from wheezy.validation.mixin import ErrorsMixin, ValidationMixin
from wheezy.validation.rules import required
from wheezy.validation.validator import Validator


class MyServiceA(ErrorsMixin):
    def __init__(self):
        self.errors = {}


class MyServiceB(ValidationMixin):
    def __init__(self):
        self.errors = {}
        self.translations = {"validation": None}


class ErrorMixinTestCase(unittest.TestCase):
    def test_errors(self):
        """Ensure error summary."""
        s = MyServiceA()
        s.error("error-message-1")
        assert {"__ERROR__": ["error-message-1"]} == s.errors

        s.error("error-message-2")
        assert [
            ("__ERROR__", ["error-message-1", "error-message-2"])
        ] == sorted(s.errors.items())

        s.error("error-message-3", "name")
        assert ["__ERROR__", "name"] == sorted(s.errors.keys())


class ValidationMixinTestCase(unittest.TestCase):
    def test_errors(self):
        """Ensure error summary."""
        s = MyServiceB()
        s.error("error-message-1")
        assert {"__ERROR__": ["error-message-1"]} == s.errors

        s.error("error-message-2")
        assert [
            ("__ERROR__", ["error-message-1", "error-message-2"])
        ] == sorted(s.errors.items())

        s.error("error-message-3", "name")
        assert ["__ERROR__", "name"] == sorted(s.errors.keys())

    def test_validate(self):
        """Ensure errors is updated by validator."""
        v = Validator({"name": [required]})
        user = {"name": "john"}
        s = MyServiceB()
        assert s.validate(user, v)
        assert not s.errors

        user = {"name": None}
        assert not s.validate(user, v)
        assert s.errors["name"]
