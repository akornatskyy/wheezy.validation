
""" ``rules`` module.
"""

_ = lambda s: s


class RequiredRule(object):

    def __init__(self, message_template=None):
        self.message_template = message_template or _(
                'Required field cannot be left blank.')

    def __call__(self, message_template):
        """ Let you customize message template.

            >>> r = required('customized')
            >>> assert r != required
            >>> r.message_template
            'customized'
        """
        return RequiredRule(message_template)

    def validate(self, value, name, model, result, ugettext):
        """
            If ``value`` is evaluated to ``False`` than it cause
            this rule to fail.

            >>> result = []
            >>> r = RequiredRule(message_template='required')
            >>> r.validate(None, None, None, result, _)
            False
            >>> result
            ['required']

            Anything that python interprets as ``True`` is passing
            this rule.

            >>> result = []
            >>> r.validate('abc', None, None, result, _)
            True
            >>> result
            []

            ``required`` is a shortcut

            >>> assert isinstance(required, RequiredRule)
        """
        if not value:
            result.append(ugettext(self.message_template))
            return False
        return True


required = RequiredRule()


class LengthRule(object):

    def __init__(self, min=None, max=None, message_template=None):
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
                self.message_template = message_template or _(
                        'Required to be a minimum of %(min)d characters'
                        ' in length.')
            else:
                self.max = max
                self.message_template = message_template or _(
                        'The length must fall within the range %(min)d'
                        ' - %(max)d characters.')
        else:
            if max:
                self.max = max
                self.check = self.check_max
                self.message_template = message_template or _(
                        'Exceeds maximum length of %(max)d.')
            else:
                self.check = self.succeed

    def succeed(self, value, name, model, result, ugettext):
        return True

    def check_min(self, value, name, model, result, ugettext):
        if len(value) < self.min:
            result.append(ugettext(self.message_template)
                    % {'min': self.min})
            return False
        return True

    def check_max(self, value, name, model, result, ugettext):
        if len(value) > self.max:
            result.append(ugettext(self.message_template)
                    % {'max': self.max})
            return False
        return True

    def check(self, value, name, model, result, ugettext):
        l = len(value)
        if l < self.min or l > self.max:
            result.append(ugettext(self.message_template)
                    % {'min': self.min, 'max': self.max})
            return False
        return True

    def validate(self, value, name, model, result, ugettext):
        """
            >>> r = LengthRule()

            Succeed if ``value`` is None

            >>> r.validate(None, None, None, None, _)
            True

            Since no range specified it chooses ``succeed`` strategy.

            >>> r.validate('abc', None, None, None, _)
            True

            ``check_min`` strategy fails

            >>> result = []
            >>> r = LengthRule(min=2, message_template='min %(min)d')
            >>> r.validate('a', None, None, result, _)
            False
            >>> result
            ['min 2']

            ``check_min`` strategy succeed

            >>> result = []
            >>> r = LengthRule(min=2)
            >>> r.validate('ab', None, None, result, _)
            True
            >>> result
            []

            ``check_max`` strategy fails

            >>> result = []
            >>> r = LengthRule(max=2, message_template='max %(max)d')
            >>> r.validate('abc', None, None, result, _)
            False
            >>> result
            ['max 2']

            ``check_max`` strategy succeed

            >>> result = []
            >>> r = LengthRule(max=2)
            >>> r.validate('ab', None, None, result, _)
            True
            >>> result
            []

            ``check`` strategy fails

            >>> r = LengthRule(min=2, max=3,
            ...         message_template='range %(min)d-%(max)d')
            >>> result = []
            >>> r.validate('a', None, None, result, _)
            False
            >>> result
            ['range 2-3']

            ``check`` strategy succeed

            >>> result = []
            >>> r = LengthRule(min=1, max=2)
            >>> r.validate('ab', None, None, result, _)
            True
            >>> result
            []

            ``length`` is shortcut

            >>> assert length is LengthRule
        """
        return value is None or self.check(value, name, model,
                result, ugettext)


length = LengthRule
