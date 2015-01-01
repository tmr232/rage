from _winreg import *
import types
import collections



"""
def main():
    reg = Reg.HKCU["Software\\7-Zip"]
    reg = Reg(HKCU)["Software\\7-zip"]

    reg.values -> dict
    reg.values[name] = String(value)

    reg["version"].path
"""

KeyInfo = collections.namedtuple("KeyInfo", "subkeys values modified")

class RegistryKey(object):
    def __init__(self, key, subkey=None):
        if isinstance(key, RegistryKey):
            key = key.key
        self._key = OpenKey(key, subkey)

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


def enum_key_values(key):
    subkeys, values, modified = QueryInfoKey(key)
    for index in xrange(values):
        yield EnumValue(key, index)


if __name__ == '__main__':

    key = OpenKey(HKEY_CLASSES_ROOT, None)
    subkey = OpenKey(key, ".txt")
    print QueryInfoKey(key)
    print QueryInfoKey(subkey)

    key = RegistryKey(HKEY_CLASSES_ROOT, None)
    subkey = key[".txt"]
    print key.get_info()
    print subkey.get_info()


    for value in subkey.enum_values():
        print value

    for key in subkey.enum_keys():
        print key