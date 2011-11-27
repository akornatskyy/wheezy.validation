
""" ``comp`` module.
"""

import sys


PY3 = sys.version_info[0] >= 3

if PY3:  # pragma: nocover
    iterkeys = lambda d: d.keys()
    iteritems = lambda d: d.items()
    copyitems = lambda d: list(d.items())
else:  # pragma: nocover
    iterkeys = lambda d: d.iterkeys()
    iteritems = lambda d: d.iteritems()
    copyitems = lambda d: d.items()


from gettext import NullTranslations
null_translations = NullTranslations()

if PY3:  # pragma: nocover
    ref_gettext = lambda t: t.gettext
else:  # pragma: nocover
    ref_gettext = lambda t: t.ugettext
