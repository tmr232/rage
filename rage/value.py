from _winreg import REG_SZ, REG_EXPAND_SZ, REG_BINARY, REG_DWORD, REG_MULTI_SZ
import types



class RegValue(object):
    """
    Baseclass for registry values.
    Only used as baseclass.
    """

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


def parse_value(named_reg_value):
    """
    Convert the value returned from EnumValue to a (name, value) tuple using the value classes.
    """
    name, value, value_type = named_reg_value
    value_class = REG_VALUE_TYPE_MAP[value_type]
    return name, value_class(value)


class ValueHandler(object):
    def __init__(self, key):
        self._key = key

    def __getitem__(self, name):
        # Get item by its name.
        if isinstance(name, types.StringTypes):
            for value_name, value in self._key._iter_values():
                if value_name == name:
                    return value

        # Get an item by its index. Provided to support the sequence protocol.
        elif isinstance(name, types.IntType):
            try:
                return self._key._enum_value(name)
            except WindowsError as e:
                # On exception, make sure it is the last value and raise StopIteration.
                if e.winerror != 259:
                    raise
                if not name < self._key.get_info().values:
                    raise StopIteration()

        raise ValueError(name)

    def __setitem__(self, name, value):
        self._key.set_value(name, value)

    def __delitem__(self, name):
        self._key.delete_value(name)

    def __len__(self):
        return self._key.get_info().values



REG_VALUE_TYPE_MAP = {cls.TYPE: cls for cls in (RegSZ, RegExpandSZ, RegBinary, RegDword, RegMultiSZ)}
