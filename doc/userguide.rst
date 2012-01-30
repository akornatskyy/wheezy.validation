
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
criterion used in the process of data validation.

There are a number of validation rules defined already.

* ``required``. Any value evaluated to boolean ``True`` pass this rule. See
  :py:class:`~wheezy.validation.rules.RequiredRule`.
* ``length``. Result of python function ``len()`` must fall within a range
  defined by this rule. Supported range attributes include: ``min``, ``max``.
  See :py:class:`~wheezy.validation.rules.LengthRule`.
* ``compare``. Compares attribute being validated with some other attribute
  value. Supported comparison operations include: ``equal``. See 
  :py:class:`~wheezy.validation.rules.CompareRule`.

Custom Message
~~~~~~~~~~~~~~
  
You are able customize error message by using ``message_template`` argument
during rule declaration::

    credential_validator = Validator({
        'username': [required(message_template='Required field')]
    })

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
   :lines: 11-18

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

