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
    def wrapper(self, *args, **kwargs):
        if not self._edit:
            raise RegistryKeyNotEditable("The key is not set as editable.")
        return f(self, *args, **kwargs)

    return wrapper


class RegValue(object):
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def value_type(self):
        return self.TYPE

    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            repr(self.value)
        )


class RegSZ(RegValue):
    TYPE = REG_SZ


class RegExpandSZ(RegValue):
    TYPE = REG_EXPAND_SZ


class RegBinary(RegValue):
    TYPE = REG_BINARY


class RegDword(RegValue):
    TYPE = REG_DWORD


class RegMultiSZ(RegValue):
    TYPE = REG_MULTI_SZ


REG_VALUE_TYPE_MAP = {cls.TYPE: cls for cls in (RegSZ, RegExpandSZ, RegBinary, RegDword, RegMultiSZ)}


def parse_value(named_reg_value):
    name, value, value_type = named_reg_value
    value_class = REG_VALUE_TYPE_MAP[value_type]
    return name, value_class(value)


class ValueHandler(object):
    def __init__(self, key):
        self._key = key

    def __getitem__(self, name):
        if isinstance(name, types.StringTypes):
            for value_name, value in self._key.enum_values():
                if value_name == name:
                    return value
        elif isinstance(name, types.IntType):
            try:
                return self._key._enum_value(name)
            except WindowsError as e:
                if e.winerror != 259:
                    raise
                if not name < self._key.get_info().values:
                    raise StopIteration()

        raise ValueError(name)

    def __setitem__(self, name, value):
        self._key.set_value(name, value)

    def __len__(self):
        return self._key.get_info().values


class RegistryKey(object):
    def __init__(self, key, subkey=None, edit=False):
        if subkey is None:
            subkey = ""

        self._open_key(key, subkey, edit=edit)

        base_path = self._get_key_path(key)
        self._path = os.path.join(base_path, subkey)

        self._edit = edit

    @require_editable
    def set_value(self, name, value):
        SetValueEx(self.key, name, 0, value.value_type, value.value)


    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            repr(self.path)
        )

    def _open_key(self, key, subkey, edit=False):
        hkey = key
        if isinstance(key, RegistryKey):
            hkey = key.key

        elif isinstance(key, types.StringTypes):
            hkey, subkey = self._parse_key(key, subkey)

        if edit:
            options = KEY_READ_WRITE
        else:
            options = KEY_READ
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
        return self._path

    @property
    def key(self):
        return self._key

    def __getitem__(self, subkey):
        return RegistryKey(self, subkey)

    def get_info(self):
        return KeyInfo(*QueryInfoKey(self.key))

    def _enum_value(self, index):
        return parse_value(EnumValue(self.key, index))

    def enum_values(self):
        subkeys, values, modified = self.get_info()
        for index in xrange(values):
            yield self._enum_value(index)

    @property
    def values(self):
        return ValueHandler(self)

    def _enum_key(self, index):
        return EnumKey(self.key, index)

    def enum_keys(self):
        subkeys, values, modified = self.get_info()
        for index in xrange(subkeys):
            yield self._enum_key(index)

    def _parse_key(self, key, subkey):
        if not isinstance(key, types.StringTypes):
            return key, subkey

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


def enum_key_values(key):
    subkeys, values, modified = QueryInfoKey(key)
    for index in xrange(values):
        yield EnumValue(key, index)


if __name__ == '__main__':
    key = RegistryKey(r"HKEY_CURRENT_USER\Tamir", edit=True)
    print list(key.enum_values())
    key.set_value("a", RegSZ("a"))
    key.set_value("b", RegExpandSZ("x"))
    key.set_value("c", RegMultiSZ(["a", "s", "c"]))
    print key.get_info()
    print list(key.values)
    key.values["a"] = RegSZ("This works!")