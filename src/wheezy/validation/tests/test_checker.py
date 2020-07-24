""" Unit tests for ``wheezy.validation.checker``.
"""

import unittest

from wheezy.validation.rules import compare, email, length, one_of, required
from wheezy.validation.validator import Validator

# region: validation rules

account_validator = Validator(
    {
        "email": [required, length(min=6), length(max=30), email],
        "account_type": [required, one_of(("user", "business"))],
    }
)

password_match_validator = Validator(
    {
        "password": [
            compare(
                equal="confirm_password",
                message_template="Passwords do not match.",
            )
        ]
    }
)


# region: unit tests


class AccountValidatorTestCase(unittest.TestCase):
    def setUp(self):
        from wheezy.validation.checker import Checker

        self.c = Checker(gettext=lambda t: str(t))
        self.c.use(account_validator)

    def test_email(self):
        assert not self.c.error(email="johh@somewhere.net")

        e = "Required field cannot be left blank."
        assert e == self.c.error(email="")
        e = "Required to be a minimum of 6 characters in length."
        assert e == self.c.error(email="x" * 5)
        e = "Exceeds maximum length of 30."
        assert e == self.c.error(email="x" * 31)
        e = "Required to be a valid email address."
        assert e == self.c.error(email="x@somewhere")

    def test_account_type(self):
        for account_type in ("user", "business"):
            assert not self.c.error(account_type=account_type)

        e = "Required field cannot be left blank."
        assert e == self.c.error(account_type="")
        e = "The value does not belong to the list of known items."
        assert e == self.c.error(account_type="x")


class PasswordMatchValidatorTestCase(unittest.TestCase):
    def setUp(self):
        from wheezy.validation.checker import Checker

        self.c = Checker(gettext=lambda t: str(t))
        self.c.use(
            "wheezy.validation.tests.test_checker." "password_match_validator"
        )

    def test_password(self):
        assert not self.c.error(password="x", confirm_password="x")

        e = "Passwords do not match."
        assert e == self.c.error(password="x", confirm_password="")


class AccountValidatorAllErrorsTestCase(unittest.TestCase):
    def setUp(self):
        from wheezy.validation.checker import Checker

        self.c = Checker(stop=False, gettext=lambda t: str(t))
        self.c.use(account_validator)

    def test_email(self):
        assert not self.c.errors(email="johh@somewhere.net")

        e = "Required to be a valid email address."
        assert e == self.c.error(email="")
        assert [
            "Required field cannot be left blank.",
            "Required to be a minimum of 6 characters in length.",
            "Required to be a valid email address.",
        ] == self.c.errors(email="")


class ModelTestCase(unittest.TestCase):
    def test_items(self):
        from wheezy.validation.checker import Model

        m = Model(a=1, b=2)
        assert [("a", 1), ("b", 2)] == sorted(m.items())
        assert 1 == m.a
        assert 1 == m["a"]
        assert 2 == m.b
        assert m.c is None
        assert m["d"] is None
