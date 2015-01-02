Rage
====

Easy Windows-Registry display & manipulation in Python.

.. code:: python

    from rage import RegistryKey, RegSZ

    # Open some key
    key = RegistryKey(some_registry_path)

    # Print names of all subkeys
    for key_name in key.enum_keys():
        print key

    # Get a subkey
    subkey = key["subkey-name"]

    # Print out all the subkey's values
    for name, value in subkey.values:
        print repr(name), value

    # Set one of the values
    editable_subkey = subkey.get_editable()
    editable_subkey.values["my value name"] = RegSZ("Value value!")

    # Delete a value
    del editable_subkey.values["value to delete"]

    # Delete a subkey
    editable_subkey.delete_subkey("subkey name", recurse=False)