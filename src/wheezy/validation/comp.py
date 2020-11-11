""" ``comp`` module.
"""


def ref_getter(model):
    # if model is a dict
    if hasattr(model, "__iter__"):
        return type(model).__getitem__
    else:
        return getattr
