
Examples
========

We start with a simple credential validation example. Before we proceed 
let setup `virtualenv`_ environment::

    $ virtualenv env
    $ env/bin/easy_install wheezy.validation


.. _helloworld:

Credential Validation
---------------------

Domain Model
~~~~~~~~~~~~

Our domain model requires that user enter valid credentials during sigin, so
``Credential`` model might look like this::

    class Credential(object):

        def __init__(self):
            self.username = ''
            self.password = ''

Validator
~~~~~~~~~

We know that username is a string between 2 and 20 in length, while password
must have at least 8 characters and we would like limit it by 12. Both username
and password are required and we need a separate message for this case. Here
is ``credential_validator`` that serves our purpose::

    from wheezy.validation import Validator
    from wheezy.validation.rules import length
    from wheezy.validation.rules import required


    credential_validator = Validator({
        'username': [required, length(min=2, max=20)],
        'password': [required, length(min=8, max=12)]
    })

Since validator in no way dependent on object it is going to validate, it can 
be reused in any combination, the only requirement that attributes defined
in validator must exist in object you are going to validate.

Validation
~~~~~~~~~~

Now we can proceed with validation::
    
    credential = Credential()
    errors = {}
    succeed = credential_validator.validate(credential, results=errors)

``errors`` dictionary contains all errors reported during validation. Key
corresponds to attribute being checked, while value is a list of errors.

Credential Update
-----------------

Web form submit is a dictionary where key is the name of the input element
being submitted and value is a list. That list can have just one item for
elements like input or several values that depict user choice.

Let assume form submitted values look this way::

    values = {'username': [''], 'password': ['']}

Our attempt to update ``Credential`` model with ``values``::
    
    credential = Credential()
    errors = {}
    succeed = try_update_model(credential, values, errors)

``errors`` dictionary contains all errors reported during model update. Key
corresponds to attribute being updated, while value is a list of errors.

.. _`virtualenv`: http://pypi.python.org/pypi/virtualenv
