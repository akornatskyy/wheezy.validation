import unittest

from wheezy.validation.rules import length, required
from wheezy.validation.validator import Validator


class User(object):
    name = None


class Registration(object):
    def __init__(self):
        self.user = User()


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.v = Validator({"name": [required, length(min=4)]})

    def test_stop_on_first_fail(self):
        """Validation stops on fist fail."""
        errors = {}
        u = User()

        assert not self.v.validate(u, errors)
        assert 1 == len(errors["name"])

        u.name = "abc"
        errors = {}
        assert not self.v.validate(u, errors)
        assert 1 == len(errors["name"])

    def test_all_that_fail(self):
        """All fails by settings optional ``stop`` to ``False``."""
        errors = {}
        u = User()

        u.name = ""
        assert not self.v.validate(u, errors, stop=False)
        assert 2 == len(errors["name"])

    def test_nested(self):
        """Validator can nest other validator for composite objects."""
        rv = Validator({"user": self.v})

        errors = {}
        r = Registration()
        assert not rv.validate(r, errors)
        assert errors
        assert 1 == len(errors["name"])

    def test_validation_succeed(self):
        """Validation succeed for valid input."""
        rv = Validator({"user": self.v})

        errors = {}
        u = User()

        u.name = "john"
        assert self.v.validate(u, errors)
        assert not errors

        r = Registration()
        r.user.name = "john"
        assert self.v.validate(r.user, errors)
        assert not errors

        assert rv.validate(r, errors)
        assert not errors

    def test_validate_dict(self):
        """Validatable can be a python dict object."""
        errors = {}
        u = {"name": None}
        assert not self.v.validate(u, errors)
        assert errors

        errors = {}
        u["name"] = "john"
        assert self.v.validate(u, errors)
        assert not errors
