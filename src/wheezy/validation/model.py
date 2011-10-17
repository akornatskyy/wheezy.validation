
""" ``model`` module.
"""

from decimal import Decimal


CONVERTERS = {
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

        >>> #from timeit import timeit
        >>> #timeit(lambda: try_update_model(user, values,
        ... #    results), number=100000)
    """
    for name in model.__dict__:
        attr = getattr(model, name)
        converter = CONVERTERS[type(attr).__name__]
        if converter:
            value = values[name]
            try:
                value = converter(value[-1])
            except ArithmeticError:
                results[name] = ['invalid_value']
            else:
                setattr(model, name, value)
    return True
