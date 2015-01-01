from _winreg import *
import types
import collections
import os.path


"""
def main():
    reg = Reg.HKCU["Software\\7-Zip"]
    reg = Reg(HKCU)["Software\\7-zip"]

    reg.values -> dict
    reg.values[name] = String(value)

    reg["version"].path
"""

KeyInfo = collections.namedtuple("KeyInfo", "subkeys values modified")

ROOT_NAMES = {
    HKEY_CLASSES_ROOT: "HKEY_CLASSES_ROOT",
    HKEY_CURRENT_USER: "HKEY_CURRENT_USER",
    HKEY_LOCAL_MACHINE: "HKEY_LOCAL_MACHINE",
    HKEY_CURRENT_CONFIG: "HKEY_CURRENT_CONFIG",
    HKEY_USERS: "HKEY_USERS"
}

REVERSE_ROOT_NAMES = {value: key for key, value in ROOT_NAMES.iteritems()}


class RegistryKey(object):
    def __init__(self, key, subkey=None):
        if subkey is None:
            subkey = ""

        self._open_key(key, subkey)

        base_path = self._get_key_path(key)
        self._path = os.path.join(base_path, subkey)

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            repr(self.path)
        )

    def _open_key(self, key, subkey):
        hkey = key
        if isinstance(key, RegistryKey):
            hkey = key.key

        elif isinstance(key, types.StringTypes):
            hkey, subkey = self._parse_key(key, subkey)
        self._key = OpenKey(hkey, subkey)

    def _get_key_path(self, key):
        if isinstance(key, RegistryKey):
            return key.path
        elif isinstance(key, types.StringTypes):
            return key
        else:
            return ROOT_NAMES[key]

    @property
    def path(self):
        return self._path

    @property
    def key(self):
        return self._key

    def __getitem__(self, subkey):
        return RegistryKey(self, subkey)

    def get_info(self):
        return KeyInfo(*QueryInfoKey(self.key))

    def _enum_value(self, index):
        return EnumValue(self.key, index)

    def enum_values(self):
        subkeys, values, modified = self.get_info()
        for index in xrange(values):
            yield self._enum_value(index)

    def _enum_key(self, index):
        return EnumKey(self.key, index)

    def enum_keys(self):
        subkeys, values, modified = self.get_info()
        for index in xrange(subkeys):
            yield self._enum_key(index)

    def _parse_key(self, key, subkey):
        if not isinstance(key, types.StringTypes):
            return key, subkey

        base, path = os.path.split(key)
        if base:
            print base
            hkey = REVERSE_ROOT_NAMES[base]
            subkey_path = os.path.join(path, subkey)
        else:
            print path
            hkey = REVERSE_ROOT_NAMES[path]
            subkey_path = subkey

        return hkey, subkey_path



def enum_key_values(key):
    subkeys, values, modified = QueryInfoKey(key)
    for index in xrange(values):
        yield EnumValue(key, index)


if __name__ == '__main__':
    print REVERSE_ROOT_NAMES
    key = OpenKey(HKEY_CLASSES_ROOT, None)
    subkey = OpenKey(key, ".txt")
    print QueryInfoKey(key)
    print QueryInfoKey(subkey)

    key = RegistryKey("HKEY_CLASSES_ROOT", None)
    subkey = key[".txt"]
    print key.get_info()
    print subkey.get_info()

    print key
    print subkey

    for value in subkey.enum_values():
        print value

    for key in subkey.enum_keys():
        print key