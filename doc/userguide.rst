
User Guide
==========

Users fill the web form with necessary information, however, they often make
mistakes. This is where form validation comes into play. The goal of
validation is to ensure that the user provided necessary and properly
formatted information needed to successfully complete an operation.

Validator
---------

:py:class:`~wheezy.validation.validator.Validator` is a container of validation
rules that all together provide object validation. You instantiate
:py:class:`~wheezy.validation.validator.Validator` and supply it a map
between attribute names being validated and list of rules. Here is an example::

    credential_validator = Validator({
        'username': [required, length(max=10)],
        'password': [required, length(min=8, max=12)]
    })

:py:class:`~wheezy.validation.validator.Validator` in no way tied to object
and/or class being validated, instead the only requirement is existance of
attributes being validated.

:py:class:`~wheezy.validation.validator.Validator` supports
``__getitem__`` interface, so is applicable to ``dict`` like objects::

    user = {'username': '', 'password': ''}
    errors = {}
    succeed = credential_validator.validate(user, errors)

Method ``validate`` returns ``True`` only in case all validation rules succeed
otherwise ``False``.

``errors`` dictionary contains all errors reported during validation. Key
corresponds to attribute name being checked, while value is a list of errors.

If you need validation check all rules for failed attribute, you need set
``stop`` attribute to ``False`` (default is to stop on first error)::

    succeed = credential_validator.validate(user, errors, stop=False)

Nested Validator
~~~~~~~~~~~~~~~~

:py:class:`~wheezy.validation.validator.Validator` can be nested into the
other validator so ultimately can form any hierarchically complex structure.
This can be useful for composite objects, e.g. ``Registration`` model can
aggregate ``Credential`` model. While each model has own validation,
registration model can nest validator for credential model::

    class Registration(object):
        def __init__(self):
            self.credential = Credential()

    registration_validator = Validator({
        'credential': credential_validator
    })

Internationalization
~~~~~~~~~~~~~~~~~~~~

:py:class:`~wheezy.validation.validator.Validator` supports python standard
``gettext`` module. You need to pass ``gettext`` translations as a argument
to ``validate`` method. Here is an example::

    from gettext import NullTranslations

    translations = NullTranslations()
    succeed = credential_validator.validate(
            user,
            errors,
            translations=translations)

Thread Safety
~~~~~~~~~~~~~

Validator does not alter it state once initialized. It is guaranteed to be
thread safe.

Validation Rules
----------------

Validation rules prevent bad data being processed. A validation rule is a
criterion used in the process of data validation. Rules support simple types
as well as list types of attributes, e.g. ``iterator`` rule can apply
a number of other rules to each item in the list.

There are a number of validation rules defined already.

* ``required``. Any value evaluated to boolean ``True`` pass this rule.
  Take also a look at ``required_but_missing`` list. See
  :py:class:`~wheezy.validation.rules.RequiredRule`.
* ``missing``. Any value evaluated to boolean ``False`` pass this
  rule. Take also a look at ``required_but_missing`` list. See
  :py:class:`~wheezy.validation.rules.RequiredRule`.
* ``length``. Result of python function ``len()`` must fall within a range
  defined by this rule. Supported range attributes include: ``min``, ``max``.
  See :py:class:`~wheezy.validation.rules.LengthRule`.
* ``compare``. Compares attribute being validated with some other attribute
  value. Supported comparison operations include: ``equal``,
  ``not_equal``. See :py:class:`~wheezy.validation.rules.CompareRule`.
* ``predicate``, ``model_predicate``. Fails if predicate return
  boolean ``False``. Predicate is any callable that accepts model and
  returns a boolean. It is useful for custom rules, e.g. a number of
  days between two model properties must not exceed certain value, etc.
  See :py:class:`~wheezy.validation.rules.PredicateRule`.
* ``must``, ``value_predicate``. Fails if predicate return
  boolean ``False``. Predicate is any callable that accepts a value and
  returns a boolean. It is useful for custom rule applicable to
  multiple attributes of model.
  See :py:class:`~wheezy.validation.rules.ValuePredicateRule`.
* ``regex``. Search for regular expression pattern. Initialized with
  ``regex`` as a regular expression pattern or a pre-compiled regular
  expression. Supports ``nagated`` argument.
  See :py:class:`~wheezy.validation.rules.RegexRule`.
* ``slug``. Ensures only letters, numbers, underscores or hyphens. See
  :py:class:`~wheezy.validation.rules.SlugRule`.
* ``email``. Ensures a valid email. See
  :py:class:`~wheezy.validation.rules.EmailRule`.
* ``range``. Ensures value is in range defined by this rule. Works with any
  numbers including int, float, decimal, etc. Supported range attributes
  include: ``min``, ``max``. See
  :py:class:`~wheezy.validation.rules.RangeRule`.
* ``and_``. Applies all ``rules`` regardless of validation result. See
  :py:class:`~wheezy.validation.rules.AndRule`.
* ``or_``. Succeeds if at least one rule in ``rules`` succeed. Failed rule
  results are not added unless they all fail. See
  :py:class:`~wheezy.validation.rules.OrRule`.
* ``iterator``. Applies ``rules`` to each item in value. Iterates over each
  rule and checks whenever any item in value fails. Designed to work with
  iteratable attributes: list, tuple, etc. See
  :py:class:`~wheezy.validation.rules.IteratorRule`.
* ``one_of``. Value must match at least one element from ``items``. Checks
  whenever value belongs to ``items``. See
  :py:class:`~wheezy.validation.rules.OneOfRule`.
* ``relative_date``, ``relative_utcdate``, ``relative_tzdate``,
  ``relative_datetime``, ``relative_utcdatetime``,
  ``relative_tzdatetime``. Check if value is in relative
  date/datetime range per local, UTC or tz time. See
  :py:class:`~wheezy.validation.rules.RelativeDateDeltaRule`,
  :py:class:`~wheezy.validation.rules.RelativeUTCDateDeltaRule`,
  :py:class:`~wheezy.validation.rules.RelativeTZDateDeltaRule` and
  :py:class:`~wheezy.validation.rules.RelativeDateTimeDeltaRule`,
  :py:class:`~wheezy.validation.rules.RelativeUTCDateTimeDeltaRule`,
  :py:class:`~wheezy.validation.rules.RelativeTZDateTimeDeltaRule`.
* ``ignore``. The idea behind this rule is to be able to substitute
  any validation rule by this one that always succeed. See
  :py:class:`~wheezy.validation.rules.IgnoreRule`

Custom Message
~~~~~~~~~~~~~~

You are able customize error message by using ``message_template`` argument
during rule declaration::

    credential_validator = Validator({
        'username': [required(message_template='Required field')]
    })

Every rule supports ``message_template`` argument during rule declaration.

``gettext`` utilities
^^^^^^^^^^^^^^^^^^^^^

Please remember to add ``msgid``/``msgstr`` of customized validation error to
``po`` file. You can extract gettext messages by::

    $ xgettext --join-existing --sort-by-file --omit-header \
		-o i18n/translations.po src/*.py

Compile po files::

    $ msgfmt -v translations.po -o translations.mo

Custom Rules
~~~~~~~~~~~~

It is easy to provide own validation rule. The rule is any callable of the
following contract::

    def check(self, value, name, model, result, gettext):

Here is a description of each attribute:

* ``value`` - value that is currently validated.
* ``name`` - name of attribute.
* ``model`` - object being validated.
* ``result`` - a dictionary that accepts validation errors.
* ``gettext`` - a function used to provide i18n support.

Validation Mixin
----------------
:py:class:`~wheezy.validation.mixin.ValidationMixin` provides sort of
contextual integration with third party modules. Specifically this mixin
requires two attributes: ``errors`` and ``translations``. Once these two
attributes provided, validation can be simplified. Let review it by example::

    user_validator = Validator({
        'name': [required]
    })

We defined ``user_validator``. Now here is our integration in some service::

    class MyService(ValidationMixin):

         def __init__(self):
             self.errors = {}
             self.translations = {'validation': None}

         def signin(self, user):
             succeed = self.validate(user, user_validator)
             ...
             self.error('Unauthorized')
             return False

If the ``signin`` operation fails the client can request all validation errors
from  ``errors`` attribute. Note that general error message ('Unauthorized')
is stored under ``__ERROR__`` key. Thus can be used to display general
information to end user.

Model Update
------------
Web form submit is a dictionary where key is the name of the input element
being submitted and value is a list. That list can have just single value for
elements like input or several values that depict user choice.

:py:meth:`~wheezy.validation.model.try_update_model` method is provided to
try update any given object with values submitted by web form.

The convention used by :py:meth:`~wheezy.validation.model.try_update_model`
method is requirement for the model to be properly initialized with default
values, e.g. integer attributes must default to some integer value, etc.

List of supported ``value_providers``:

.. literalinclude:: ../src/wheezy/validation/model.py
   :lines: 203-213

Example of domain model initialized with defaults::

    class Credential(object):

        def __init__(self):
            self.username = ''
            self.password = ''

Values submitted by web form::

    values = {'username': [''], 'password': ['']}

Typical use case as follows::

    credential = Credential()
    errors = {}
    succeed = try_update_model(credential, values, errors)

``errors`` dictionary contains all errors reported during model update. Key
corresponds to attribute being updated, while value is a list of errors.

Numbers
~~~~~~~

Number value providers (
:py:meth:`~wheezy.validation.model.int_value_provider`,
:py:meth:`~wheezy.validation.model.decimal_value_provider`,
:py:meth:`~wheezy.validation.model.float_value_provider`) support thousands
separator as well as decimal separator. Take a look at ``validation.po`` file.

Date and Time
~~~~~~~~~~~~~
Date and time value providers (
:py:meth:`~wheezy.validation.model.date_value_provider`,
:py:meth:`~wheezy.validation.model.time_value_provider`,
:py:meth:`~wheezy.validation.model.datetime_value_provider`) support a number
of formats. Generally there is default format and fallback formats. It tries
default format and if it fails tries fallback formats. Take a look at
``validation.po`` file for a list of supported format.

Please note that :py:meth:`~wheezy.validation.model.datetime_value_provider`
fallback to :py:meth:`~wheezy.validation.model.date_value_provider` in case
none of its own formats matched. Empty value is converted to minimal value
for date/time.

Lists
~~~~~

:py:meth:`~wheezy.validation.model.try_update_model` method supports list
attributes. Note that existing model list is used (it is not overwritten).

    >>> class User(object):
    ...     def __init__(self):
    ...         self.prefs = []
    ...         self.prefs2 = [0]
    >>> user = User()
    >>> values = {'prefs': ['1', '2'], 'prefs2': ['1', '2']}
    >>> results = {}
    >>> try_update_model(user, values, results)
    True
    >>> user.prefs
    ['1', '2']
    >>> user.prefs2
    [1, 2]

Note that the type of the first element in the list selects value_provider
for all elements in the list.

Custom Value Providers
~~~~~~~~~~~~~~~~~~~~~~

Value provider is any callable of the following contract::

    def my_value_provider(str_value, gettext):
        return parsed_value

You can add your value provider to defaults::

    from wheezy.validation.model import value_providers

    value_providers['my_type'] = my_value_provider
