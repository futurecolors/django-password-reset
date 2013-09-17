Django-password-reset
=====================

.. image:: https://travis-ci.org/futurecolors/django-password-reset.png?branch=master
   :target: https://travis-ci.org/futurecolors/django-password-reset

.. image:: https://coveralls.io/repos/futurecolors/django-password-reset/badge.png?branch=master
    :target: https://coveralls.io/r/futurecolors/django-password-reset/

Class-based views for password reset, the usual "forget password?" workflow:

* User fills his email address or username
* Django sends him an email with a token to reset his password
* User chooses a new password

The token is not stored server-side, it is generated using Django's signing
functionality.

* Author: Bruno Renié and `contributors`_
* Licence: BSD
* Compatibility: Django 1.4+ (cryptographic signing needed)

.. _contributors: https://github.com/brutasse/django-password-reset/contributors

Installation
------------

* ``pip install -U django-password-reset``
* Add ``password_reset`` to your ``INSTALLED_APPS``
* Include ``password_reset.urls`` in your root ``urls.py``

For extensive documentation see the ``docs`` folder or `read it on
readthedocs`_

.. _read it on readthedocs: http://django-password-reset.readthedocs.org/

To install the `in-development version`_ of django-password-reset, run ``pip
install django-password-reset==dev``.

.. _in-development version: https://github.com/brutasse/django-password-reset/tarball/master#egg=django-password-reset-dev

Changelog
---------

0.6.x
~~~~~
* fail_noexistent_user option to make resetting password more secure
* fail_inactive_user option to restrict inactive users from resetting password

0.5.x
~~~~~
* Added django-templated-email for sending email
