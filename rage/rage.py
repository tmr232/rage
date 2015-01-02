from _winreg import *
import types
import collections
import os.path


# Privileges required for opening keys
from value import parse_value, ValueHandler

KEY_READ = 0x20019
KEY_WRITE = 0x20006
KEY_READ_WRITE = KEY_READ | KEY_WRITE

KeyInfo = collections.namedtuple("KeyInfo", "subkeys values modified")
NamedValue = collections.namedtuple("NamedValue", "name value value_type")

ROOT_NAMES = {
    HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
    HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
    HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
    HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG",
    HKEY_USERS: "HKEY_USERS"
}

REVERSE_ROOT_NAMES = {value: key for key, value in ROOT_NAMES.iteritems()}


class RegistryKeyNotEditable(Exception): pass


def require_editable(f):
    """
    Makes sure the registry key is editable before trying to edit it.
    """

    def wrapper(self, *args, **kwargs):
        if not self._edit:
            raise RegistryKeyNotEditable("The key is not set as editable.")
        return f(self, *args, **kwargs)

    return wrapper


class RegistryKey(object):
    def __init__(self, key, subkey=None, edit=False):
        """
        edit - Whether the key is editable or not. Will affect subkey access as well.
        """
        if subkey is None:
            subkey = ""

        self._open_key(key, subkey, edit=edit)

        base_path = self._get_key_path(key)
        self._path = os.path.join(base_path, subkey)

        self._edit = edit

    def __repr__(self):
        return "{}({}, edit={})".format(
            self.__class__.__name__,
            repr(self.path),
            self._edit
        )

    def __getitem__(self, subkey):
        return self.open_subkey(subkey, edit=self._edit)


    @require_editable
    def set_value(self, name, value):
        SetValueEx(self.key, name, 0, value.value_type, value.value)

    @require_editable
    def delete_value(self, value_name):
        DeleteValue(self._key, value_name)

    def _open_key(self, key, subkey, edit=False):
        # Get a key-subkey pair, `key` can be a key, a string or an instance.
        hkey, subkey = self._parse_key(key, subkey)

        # Set key permissions
        if edit:
            options = KEY_READ_WRITE
        else:
            options = KEY_READ

        # Open the key
        self._key = OpenKeyEx(hkey, subkey, 0, options)

    def _get_key_path(self, key):
        if isinstance(key, RegistryKey):
            return key.path
        elif isinstance(key, types.StringTypes):
            return key
        else:
            return ROOT_NAMES[key]

    @property
    def path(self):
        return self._path.strip(os.path.sep)

    @property
    def key(self):
        return self._key

    def open_subkey(self, subkey, edit=False):
        try:
            return RegistryKey(self, subkey, edit=edit)
        except WindowsError as e:
            # If the subkey cannot be found
            if e.winerror == 2:
                raise KeyError("Subkey does not exist: {}".format(
                    os.path.join(self.path, subkey)),
                )
            raise

    @require_editable
    def add_subkey(self, name):
        """
        Add a new subkey and return it.
        """
        return CreateKeyEx(self.key, name, 0, KEY_READ)

    @require_editable
    def delete_subkey(self, subkey_path, recurse=False):
        # Delete the subkey's subkeys
        if recurse:
            subkey = self[subkey_path]
            for name in subkey.iter_subkey_names():
                subkey.delete_subkey(name)

        # Delete the subkey
        DeleteKey(self.key, subkey_path)

    def get_editable(self):
        """
        Get an editable copy of the key.
        Will open the key.
        """
        return RegistryKey(self, subkey=None, edit=True)

    def get_non_editable(self):
        """
        Get an non-editable copy of the key.
        Will open the key.
        """
        return RegistryKey(self, subkey=None, edit=False)

    def get_info(self):
        return KeyInfo(*QueryInfoKey(self.key))

    def _enum_value(self, index):
        return parse_value(EnumValue(self.key, index))

    def _iter_values(self):
        subkeys, values, modified = self.get_info()
        for index in xrange(values):
            yield self._enum_value(index)

    @property
    def values(self):
        return ValueHandler(self)

    def _get_key_by_index(self, index):
        return EnumKey(self.key, index)

    def iter_subkey_names(self):
        subkeys, values, modified = self.get_info()
        for index in xrange(subkeys):
            yield self._get_key_by_index(index)

    def iter_subkeys(self, edit=False):
        for subkey_name in self.iter_subkey_names():
            return self.open_subkey(subkey_name, edit=edit)

    def get_parent_key(self):
        path = self.path

        try:
            parent, current = path.rstrip(os.path.sep).rsplit(os.path.sep, 1)
        except:
            raise ValueError("No parent key.")

        return RegistryKey(key=parent)

    def _parse_key(self, key, subkey):
        if isinstance(key, RegistryKey):
            return key.key, subkey

        if not isinstance(key, types.StringTypes):
            return key, subkey

        # We got thus far, so `key` is a string.
        # Convert the root of the key-path to an HKEY value,
        # join the rest with the subkey path.

        parts = key.split(os.path.sep, 1)
        root = parts.pop(0)
        if parts:
            path = parts.pop(0)
        else:
            path = ""

        if root:
            print root
            hkey = REVERSE_ROOT_NAMES[root]
            subkey_path = os.path.join(path, subkey)
        else:
            print path
            hkey = REVERSE_ROOT_NAMES[path]
            subkey_path = subkey

        return hkey, subkey_path

