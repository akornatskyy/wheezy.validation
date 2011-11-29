
""" ``model`` module.
"""

from decimal import Decimal

from wheezy.validation.comp import PY3
from wheezy.validation.comp import null_translations
from wheezy.validation.comp import ref_gettext


value_providers = {
    'str': str,
    'unicode': lambda s: s.decode('utf-8'),
    'int': int,
    'Decimal': Decimal,
    'bool': bool,
    'float': float
}


if not PY3:  # pragma: nocover
    value_providers['long'] = long


def try_update_model(model, values, results, translations=None):
    """
        ``values`` - a dict of lists or strings

        >>> class User(object):
        ...     def __init__(self):
        ...         self.name = ''
        ...         self.age = 0
        ...         self.balance = Decimal(0)
        >>> user = User()
        >>> values = {'name': 'abc', 'balance': ['0.1'],
        ...     'age': [33]}
        >>> results = {}
        >>> try_update_model(user, values, results)
        True
        >>> user.name
        'abc'
        >>> assert Decimal('0.1') == user.balance
        >>> user.age
        33

        Invalid values:

        >>> values = {'balance': ['x'], 'age': ['x']}
        >>> user = User()
        >>> try_update_model(user, values, results)
        False
        >>> len(results['balance'])
        1
        >>> assert Decimal(0) == user.balance
        >>> len(results['age'])
        1
        >>> user.age
        0
    """
    if translations is None:
        translations = null_translations
    gettext = ref_gettext(translations)
    succeed = True
    for name in model.__dict__:
        attr = getattr(model, name)
        provider_name = type(attr).__name__
        try:
            value_provider = value_providers[provider_name]
            value = values[name]
            try:
                if isinstance(value, list):
                    value = value[-1]
                value = value_provider(value)
            except (ArithmeticError, ValueError):
                results[name] = [gettext(
                    "The value '%s' is invalid." % value)]
                succeed = False
            else:
                setattr(model, name, value)
        except KeyError:
            pass
    return succeed
