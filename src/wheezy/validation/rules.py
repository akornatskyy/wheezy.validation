
""" ``rules`` module.
"""


class RequiredRule(object):

    def validate(self, value, name, model, result):
        """
            If ``value`` is evaluated to ``False`` than it cause
            this rule to fail.

            >>> result = []
            >>> r = RequiredRule()
            >>> r.validate(None, None, None, result)
            False
            >>> result
            ['validation_required']

            Anything that python interprets as ``True`` is passing
            this rule.

            >>> result = []
            >>> r.validate('abc', None, None, result)
            True
            >>> result
            []

            ``required`` is a shortcut

            >>> assert isinstance(required, RequiredRule)
        """
        if not value:
            result.append('validation_required')
            return False
        return True


required = RequiredRule()


class LengthRule(object):

    def __init__(self, min=None, max=None):
        """
            Initialization selects the most appropriate validation
            strategy.

            >>> r = LengthRule(min=2)
            >>> assert r.check == r.check_min
            >>> r = LengthRule(max=2)
            >>> assert r.check == r.check_max
            >>> r = LengthRule()
            >>> assert r.check == r.succeed
            >>> r = LengthRule(min=1, max=2)
        """
        if min:
            self.min = min
            if not max:
                self.min = min
                self.check = self.check_min
            else:
                self.max = max
        else:
            if max:
                self.max = max
                self.check = self.check_max
            else:
                self.check = self.succeed

    def succeed(self, value, name, model, result):
        return True

    def check_min(self, value, name, model, result):
        if len(value) < self.min:
            result.append(('validation_length_min', {'min': self.min}))
            return False
        return True

    def check_max(self, value, name, model, result):
        if len(value) > self.max:
            result.append(('validation_length_max', {'max': self.max}))
            return False
        return True

    def check(self, value, name, model, result):
        return self.check_min(value, name, model, result) \
                and self.check_max(value, name, model, result)

    def validate(self, value, name, model, result):
        """
            >>> r = LengthRule()

            Succeed if ``value`` is None

            >>> r.validate(None, None, None, None)
            True

            Since no range specified it chooses ``succeed`` strategy.

            >>> r.validate('abc', None, None, None)
            True

            ``check_min`` strategy fails

            >>> result = []
            >>> r = LengthRule(min=2)
            >>> r.validate('a', None, None, result)
            False
            >>> result
            [('validation_length_min', {'min': 2})]

            ``check_min`` strategy succeed

            >>> result = []
            >>> r = LengthRule(min=2)
            >>> r.validate('ab', None, None, result)
            True
            >>> result
            []

            ``check_max`` strategy fails

            >>> result = []
            >>> r = LengthRule(max=2)
            >>> r.validate('abc', None, None, result)
            False
            >>> result
            [('validation_length_max', {'max': 2})]

            ``check_max`` strategy succeed

            >>> result = []
            >>> r = LengthRule(max=2)
            >>> r.validate('ab', None, None, result)
            True
            >>> result
            []

            ``check`` strategy fails

            >>> r = LengthRule(min=2, max=3)
            >>> result = []
            >>> r.validate('a', None, None, result)
            False
            >>> result
            [('validation_length_min', {'min': 2})]

            >>> result = []
            >>> r.validate('abcd', None, None, result)
            False
            >>> result
            [('validation_length_max', {'max': 3})]

            ``check`` strategy succeed

            >>> result = []
            >>> r = LengthRule(min=1, max=2)
            >>> r.validate('ab', None, None, result)
            True
            >>> result
            []

            ``length`` is shortcut

            >>> assert length is LengthRule
        """
        return value is None or self.check(value, name, model, result)


length = LengthRule
