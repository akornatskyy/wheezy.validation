
""" ``validator`` module.
"""

from wheezy.validation.comp import iteritems
from wheezy.validation.comp import iterkeys
from wheezy.validation.comp import null_translations
from wheezy.validation.comp import ref_gettext
from wheezy.validation.comp import ref_getter


class Validator(object):
    """
    """
    def __init__(self, mapping):
        self.mapping = mapping

    def validate(self, model, results, stop=True, translations=None):
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
            >>> len(results['name'])
            1
            >>> user.name = 'abc'
            >>> results = {}
            >>> v.validate(user, results)
            False

            >>> len(results['name'])
            1

            However you can get all fails by settings optional
            ``stop`` to ``False``.

            >>> user.name = ''
            >>> results = {}
            >>> v.validate(user, results, stop=False)
            False
            >>> len(results['name'])
            2

            Validation succeed

            >>> user.name = 'abcde'
            >>> results = {}
            >>> v.validate(user, results)
            True
            >>> results
            {}

            Validatable can be a dict.

            >>> user = {'name': None}
            >>> results = {}
            >>> v.validate(user, results)
            False
        """
        if translations is None:
            translations = null_translations
        gettext = ref_gettext(translations)
        succeed = True
        getter = ref_getter(model)
        for (name, rules) in iteritems(self.mapping):
            value = getter(model, name)
            result = []
            for rule in rules:
                rule_succeed = rule.validate(value, name, model,
                        result, gettext)
                succeed &= rule_succeed
                if not rule_succeed and stop:
                    break
            if result:
                results[name] = result
        return succeed
