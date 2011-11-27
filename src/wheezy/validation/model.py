
""" ``model`` module.
"""

from decimal import Decimal

from wheezy.validation.comp import null_translations


value_providers = {
    'str': str,
    'unicode': lambda s: s.decode('utf-8'),
    'int': int,
    'Decimal': Decimal,
    'bool': bool,
    'long': long,
    'float': float
}


def try_update_model(model, values, results, translations=None):
    """
        >>> class User(object):
        ...     def __init__(self):
        ...         self.name = ''
        ...         self.age = 0
        ...         self.balance = Decimal(0)
        >>> user = User()
        >>> values = {'name': ['abc'], 'balance': ['0.1'],
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
    ugettext = translations.ugettext
    succeed = True
    for name in model.__dict__:
        attr = getattr(model, name)
        value_provider = value_providers.get(type(attr).__name__, None)
        if value_provider:
            value = values.get(name, None)
            if value is not None:
                try:
                    value = value[-1]
                    value = value_provider(value)
                except (ArithmeticError, ValueError):
                    results[name] = [ugettext(
                        "The value '%s' is invalid." % value)]
                    succeed = False
                else:
                    setattr(model, name, value)
    return succeed
