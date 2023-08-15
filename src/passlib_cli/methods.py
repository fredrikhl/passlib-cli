# encoding: utf-8
""" A basic API that abstracts passlib.hash to my likings. """
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)
import logging
from collections import OrderedDict
from distutils.version import LooseVersion

import passlib
from passlib.ifc import PasswordHash
from passlib.registry import list_crypt_handlers, get_crypt_handler
from passlib.utils.handlers import HasUserContext, PrefixWrapper

logger = logging.getLogger(__name__)


# Use the 'hash' or the 'encrypt' method of passlib.ifc.PasswordHash?
if LooseVersion(passlib.__version__) >= '1.7.0':
    PASSLIB_HASH_NAME = 'hash'
else:
    PASSLIB_HASH_NAME = 'encrypt'


def requires_password(method):
    """ Check if a the given hash implementation requires a password.

    Certain (dummy) hash implementations doesn't actually hash a password, and
    therefore doesn't need password input to generate output.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to check.

    :return bool:
        Return `True` if the implementation requires a password to hash.
    """
    return not method.is_disabled


def is_supported(method):
    """ Check if a given hash implementation is supported.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to check.

    :return bool:
        Return `True` if the method is supported.
    """
    if hasattr(method, 'has_backend'):
        return method.has_backend()
    return hasattr(method, PASSLIB_HASH_NAME)


def requires_user(method):
    """ Check if a the given hash implementation requires a username.

    Username must be given to the hash method as a keyword argument, `user`.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to check.

    :return bool:
        Return `True` if the implementation requires a username parameter.
    """
    if isinstance(method, PrefixWrapper):
        return requires_user(method.wrapped)
    return issubclass(method, HasUserContext)


def get_description(method):
    """ Fetch a docstring usage hint from the method. """
    return getattr(method, '__doc__', '').split('\n')[0].strip()


def get_class_name(method):
    """ Get the implementation class name from a hash method.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to check.

    :return str:
        Return the module and class name as a dot-separated string.
    """

    if isinstance(method, PrefixWrapper):
        return get_class_name(method.wrapped)
    if not issubclass(method, PasswordHash):
        raise ValueError("method is not a password hash implementation")
    return '{0.__module__}.{0.__name__}'.format(method)


def get_settings(method):
    if isinstance(method, PrefixWrapper):
        return get_settings(method.wrapped)
    if not issubclass(method, PasswordHash):
        raise ValueError("method is not a password hash implementation")
    return set(getattr(method, 'setting_kwds', None) or ())


def make_hash(method, password, **params):
    """ Hash a password using a given implementation.

    :param passlib.ifc.PasswordHash method:
        The PasswordHash implementation to use.

    :return str:
        Return the hash cryptstring.
    """
    return getattr(method, PASSLIB_HASH_NAME)(password, **params)


class MethodWrapper(object):
    """ method wrapper. """

    def __init__(self, method):
        self.method = method

    @property
    def name(self):
        return self.method.name

    @property
    def class_name(self):
        return get_class_name(self.method)

    @property
    def description(self):
        return get_description(self.method)

    @property
    def require_password(self):
        return requires_password(self.method)

    @property
    def require_user(self):
        return requires_user(self.method)

    @property
    def settings(self):
        settings = get_settings(self.method)
        if self.require_user:
            # 'user' does not appear in the setting_kwds tuple
            settings.add('user')
        return settings

    @property
    def supported(self):
        return is_supported(self.method)

    def __call__(self, password, **params):
        if self.require_user and 'user' not in params:
            raise TypeError(
                "{0.name} requires a 'user' parameter".format(self))

        for p in params:
            if p not in self.settings:
                raise TypeError(
                    "{0.name} has no parameter {1}".format(self, p))

        return make_hash(self.method, password, **params)


# Init the hash mappings:
# attr_name -> MethodWrapper(attr_name, implementation_class)
methods = OrderedDict(
    (name, MethodWrapper(get_crypt_handler(name)))
    for name in list_crypt_handlers())


def get_method(name):
    """ Look up a MethodWrapper for a given passlib method name. """
    logger.debug("looking up method from name=%s", repr(name))
    m = methods[name]
    logger.debug("found method name=%s, method=%s", m.name, repr(m.method))
    return m


def iter_all_methods():
    """ Iterate over all passlib methods as MethodWrapper objects. """
    return iter(methods.values())


def iter_supported_methods():
    """ Iterate over supported passlib methods as MethodWrapper objects. """
    for method in iter_all_methods():
        if method.supported:
            yield method
