
""" ``model`` module.
"""

from decimal import Decimal


value_providers = {
    'str': str,
    'int': int,
    'Decimal': Decimal,
    'bool': bool,
    'long': long,
    'float': float
}


def try_update_model(model, values, results):
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
        >>> user.balance
        Decimal('0.1')
        >>> user.age
        33

        Invalid values:

        >>> values = {'balance': ['x'], 'age': ['x']}
        >>> user = User()
        >>> try_update_model(user, values, results)
        False
        >>> results['balance']
        ['invalid_value']
        >>> user.balance
        Decimal('0')
        >>> results['age']
        ['invalid_value']
        >>> user.age
        0
    """
    succeed = True
    for name in model.__dict__:
        attr = getattr(model, name)
        provider = value_providers.get(type(attr).__name__, None)
        if provider:
            value = values.get(name, None)
            if value is not None:
                try:
                    value = provider(value[-1])
                except (ArithmeticError, ValueError):
                    results[name] = ['invalid_value']
                    succeed = False
                else:
                    setattr(model, name, value)
    return succeed
