
""" ``rules`` module.
"""

import re

from wheezy.validation.comp import ref_getter
from wheezy.validation.comp import regex_pattern


_ = lambda s: s


class RequiredRule(object):
    """ Any value evaluated to boolean ``True`` pass this rule.
    """

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

    def validate(self, value, name, model, result, gettext):
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
            result.append(gettext(self.message_template))
            return False
        return True


required = RequiredRule()


class LengthRule(object):
    """ Result of python function ``len()`` must fall within a range
        defined by this rule.
    """

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

    def succeed(self, value, name, model, result, gettext):
        return True

    def check_min(self, value, name, model, result, gettext):
        if len(value) < self.min:
            result.append(gettext(self.message_template)
                    % {'min': self.min})
            return False
        return True

    def check_max(self, value, name, model, result, gettext):
        if len(value) > self.max:
            result.append(gettext(self.message_template)
                    % {'max': self.max})
            return False
        return True

    def check(self, value, name, model, result, gettext):
        l = len(value)
        if l < self.min or l > self.max:
            result.append(gettext(self.message_template)
                    % {'min': self.min, 'max': self.max})
            return False
        return True

    def validate(self, value, name, model, result, gettext):
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
                result, gettext)


length = LengthRule


class CompareRule(object):
    """ Compares attribute being validated with some other attribute value.
    """

    def __init__(self, equal=None, message_template=None):
        """
            Initialization selects the most appropriate validation
            strategy.

            >>> r = CompareRule(equal='confirm_password')
            >>> assert r.check == r.check_equal
        """
        if equal:
            self.comparand = equal
            self.check = self.check_equal
            self.message_template = message_template or _(
                    'The value failed equality comparison'
                    ' with "%(comparand)s".')

    def check(self, value, name, model, result, gettext):
        return True

    def check_equal(self, value, name, model, result, gettext):
        getter = ref_getter(model)
        comparand_value = getter(model, self.comparand)
        if value != comparand_value:
            result.append(gettext(self.message_template)
                    % {'comparand': self.comparand})
            return False
        return True

    def validate(self, value, name, model, result, gettext):
        """
            No any comparer selected

            >>> r = CompareRule()
            >>> r.validate('abc', None, None, None, _)
            True

            ``check_equal`` strategy succeed.

            >>> result = []
            >>> r = CompareRule(equal='confirm_password')
            >>> model = {
            ...         'confirm_password': 'x'
            ... }
            >>> r.validate('x', None, model, result, _)
            True

            ``check_equal`` strategy fails.

            >>> result = []
            >>> r.validate('z', None, model, result, _)
            False
        """
        return self.check(value, None, model, result, gettext)

compare = CompareRule


class RegexRule(object):
    """ Search for regular expression pattern.
    """

    def __init__(self, regex=None, message_template=None):
        """
            ``regex`` - a regular expression pattern to search for
            or a pre-compiled regular expression.

            >>> result = []
            >>> r = regex(re.compile(r'\w+'))
            >>> r.validate('x', None, None, result, _)
            True
        """
        if isinstance(regex, regex_pattern):
            self.regex = re.compile(regex)
        else:
            self.regex = regex
        self.message_template = message_template or _(
                'Enter a valid value, please.')

    def validate(self, value, name, model, result, gettext):
        """
            >>> result = []
            >>> r = RegexRule(r'\d+')
            >>> r.validate('1234', None, None, result, _)
            True
            >>> r.validate('x', None, None, result, _)
            False
        """
        if not self.regex.search(value):
            result.append(gettext(self.message_template))
            return False
        return True

regex = RegexRule


class SlugRule(RegexRule):
    """ Ensures only letters, numbers, underscores or hyphens.

        >>> r = slug
        >>> result = []
        >>> r.validate('x14', None, None, result, _)
        True
        >>> r.validate('x%', None, None, result, _)
        False
    """

    def __init__(self, message_template=None):
        super(SlugRule, self).__init__(r'^[-\w]+$', message_template or _(
        'Enter a valid slug, please. The value must consist of letters, '
        'digits, underscopes and/or hyphens.'))

    def __call__(self, message_template):
        """ Let you customize message template.

            >>> r = slug('customized')
            >>> assert r != slug
            >>> r.message_template
            'customized'
        """
        return SlugRule(message_template)

slug = SlugRule()


class EmailRule(RegexRule):
    """ Ensures a valid email.

        >>> r = email
        >>> result = []
        >>> r.validate('x.14@somewhere.org', None, None, result, _)
        True
        >>> r.validate('x%', None, None, result, _)
        False
    """

    def __init__(self, message_template=None):
        super(EmailRule, self).__init__(
                re.compile(r'[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}',
                    re.IGNORECASE),
                message_template or
                _('Enter a valid email address, please.'))

    def __call__(self, message_template):
        """ Let you customize message template.

            >>> r = email('customized')
            >>> assert r != slug
            >>> r.message_template
            'customized'
        """
        return EmailRule(message_template)

email = EmailRule()


class RangeRule(object):
    """ Ensures value is in range defined by this rule.

        Works with any numbers including decimal.

        >>> from decimal import Decimal
        >>> result = []
        >>> r = range(max=Decimal('15.79'))
        >>> r.validate(Decimal('10'), None, None, result, _)
        True
    """

    def __init__(self, min=None, max=None, message_template=None):
        """
            Initialization selects the most appropriate validation
            strategy.

            >>> r = RangeRule(min=2)
            >>> assert r.check == r.check_min
            >>> r = RangeRule(max=2)
            >>> assert r.check == r.check_max
            >>> r = RangeRule()
            >>> assert r.check == r.succeed
            >>> r = RangeRule(min=1, max=2)
        """
        if min:
            self.min = min
            if not max:
                self.min = min
                self.check = self.check_min
                self.message_template = message_template or _(
                        'Required to be greater or equal to %(min)d.')
            else:
                self.max = max
                self.message_template = message_template or _(
                        'The value must fall within the range %(min)d'
                        ' - %(max)d')
        else:
            if max:
                self.max = max
                self.check = self.check_max
                self.message_template = message_template or _(
                        'Exceeds maximum allowed value of %(max)d.')
            else:
                self.check = self.succeed

    def succeed(self, value, name, model, result, gettext):
        return True

    def check_min(self, value, name, model, result, gettext):
        if value < self.min:
            result.append(gettext(self.message_template)
                    % {'min': self.min})
            return False
        return True

    def check_max(self, value, name, model, result, gettext):
        if value > self.max:
            result.append(gettext(self.message_template)
                    % {'max': self.max})
            return False
        return True

    def check(self, value, name, model, result, gettext):
        if value < self.min or value > self.max:
            result.append(gettext(self.message_template)
                    % {'min': self.min, 'max': self.max})
            return False
        return True

    def validate(self, value, name, model, result, gettext):
        """
            >>> r = RangeRule()

            Succeed if ``value`` is None

            >>> r.validate(None, None, None, None, _)
            True

            Since no range specified it chooses ``succeed`` strategy.

            >>> r.validate(100, None, None, None, _)
            True

            ``check_min`` strategy fails

            >>> result = []
            >>> r = RangeRule(min=10, message_template='min %(min)d')
            >>> r.validate(1, None, None, result, _)
            False
            >>> result
            ['min 10']

            ``check_min`` strategy succeed

            >>> result = []
            >>> r = RangeRule(min=10)
            >>> r.validate(10, None, None, result, _)
            True
            >>> result
            []

            ``check_max`` strategy fails

            >>> result = []
            >>> r = RangeRule(max=10, message_template='max %(max)d')
            >>> r.validate(11, None, None, result, _)
            False
            >>> result
            ['max 10']

            ``check_max`` strategy succeed

            >>> result = []
            >>> r = RangeRule(max=10)
            >>> r.validate(10, None, None, result, _)
            True
            >>> result
            []

            ``check`` strategy fails

            >>> r = RangeRule(min=2, max=3,
            ...         message_template='range %(min)d-%(max)d')
            >>> result = []
            >>> r.validate(1, None, None, result, _)
            False
            >>> result
            ['range 2-3']

            ``check`` strategy succeed

            >>> result = []
            >>> r = RangeRule(min=1, max=2)
            >>> r.validate(2, None, None, result, _)
            True
            >>> result
            []

            ``length`` is shortcut

            >>> assert length is LengthRule
        """
        return value is None or self.check(value, name, model,
                result, gettext)


range = RangeRule
