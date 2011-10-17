
""" ``validator`` module.
"""

from wheezy.validation.comp import iteritems
from wheezy.validation.comp import iterkeys


class Validator(object):
    """
    """
    def __init__(self, mapping, klass=None):
        """
            If ``klass`` is supplied than mapping is checked
            against available attributes.

            >>> class User(object):
            ...     name = None
            >>> from wheezy.validation.rules import required
            >>> user_validator = Validator({
            ...	    'name': [required]
            ... }, User)
            >>> assert user_validator
        """
        assert mapping
        if klass:
            for name in iterkeys(mapping):
                assert hasattr(klass, name)
        self.mapping = mapping

    def validate(self, model, results, stop=True):
        """
            Here is a class and object we are going to validate.

            >>> class User(object):
            ...     name = None
            >>> user = User()

            setup validation

            >>> from wheezy.validation.rules import required
            >>> from wheezy.validation.rules import length
            >>> v = Validator({
            ...	    'name': [required, length(min=4)]
            ... })

            Let validate user. By default validation stops on fist
            fail.

            >>> results = {}
            >>> v.validate(user, results)
            False
            >>> results
            {'name': ['validation_required']}
            >>> user.name = 'abc'
            >>> results = {}
            >>> v.validate(user, results)
            False
            >>> results
            {'name': [('validation_length_min', {'min': 4})]}

            However you can get all fails by settings optional
            ``stop`` to ``False``.

            >>> user.name = ''
            >>> results = {}
            >>> v.validate(user, results, stop=False)
            False
            >>> results # doctest: +NORMALIZE_WHITESPACE
            {'name': ['validation_required',
                ('validation_length_min', {'min': 4})]}

            Validation succeed

            >>> user.name = 'abcde'
            >>> results = {}
            >>> v.validate(user, results)
            True
            >>> results
            {}
        """
        succeed = True
        for (name, rules) in iteritems(self.mapping):
            value = getattr(model, name)
            result = []
            for rule in rules:
                rule_succeed = rule.validate(value, name, model, result)
                succeed &= rule_succeed
                if not rule_succeed and stop:
                    break
            if result:
                results[name] = result
        return succeed
