
""" ``rules`` module.
"""


class RequiredRule(object):

    def validate(self, value, name, model, result):
        if not value:
            result.append('validation_required')
            return False
        return True


required = RequiredRule()


class LengthRule(object):

    def __init__(self, min=None, max=None):
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
        return self.check_max(value, name, model, result) \
                or self.check_min(value, name, model, result)

    def validate(self, value, name, model, result):
        return value is None or self.check(value, name, model, result)


length = LengthRule
