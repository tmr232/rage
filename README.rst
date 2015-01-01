Rage
====

Easy Windows-Registry display & manipulation in Python.

.. code:: python

    key = RegistryKey("HKEY_CLASSES_ROOT")
    subkey = key[".txt"]

    for value in subkey.enum_values():
        print value

    for key in subkey.enum_keys():
        print key