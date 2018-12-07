from collections import MutableSequence

from .schema_registry import get_python_type


class DynamicObject(object):
    """
    A type for schema objects to subclass
    """
    def __new__(cls, *args, **kwargs):
        """
        Configure the new object type with each of the sub-types specified
        """
        def get_sub_types():
            sub_types = {}
            for name, field_type in cls.__dict__.items():
                sub_types[name] = field_type
            return sub_types

        new_class = super().__new__(cls)
        new_class._sub_types = get_sub_types()
        return new_class

    def __init__(self, data):
        self._data = data
        for k, v in data.items():
            if k in self._sub_types:
                setattr(self, k, self._sub_types[k](v))


class TypedArray(MutableSequence):
    """
    An array with a specified type for each item
    """
    class Meta:
        base_type = str

    def __init__(self, data, **kwargs):
        """
        Initiate list as instance property
        """
        self._data = data
        self._list = list()
        self.extend(list(data))

    def __len__(self):
        return len(self._list)

    def __getitem__(self, i):
        return self._list[i]

    def __delitem__(self, i):
        del self._list[i]

    def __setitem__(self, i, v):
        self._list[i] = self.Meta.base_type(v)

    def insert(self, i, v):
        self._list.insert(i, self.Meta.base_type(v))

    def __str__(self):
        return str(self._list)

    def __repr__(self):
        return str(self._list)


class DynamicArray(MutableSequence):
    """
    An array that includes items of different types
    """
    def __init__(self, data, **kwargs):
        """
        Initiate list as instance property
        """
        self._data = data
        self._list = list()
        self.extend(list(data))

    def __len__(self):
        return len(self._list)

    def __getitem__(self, i):
        return self._list[i]

    def __delitem__(self, i):
        del self._list[i]

    def __setitem__(self, i, v):
        python_type = get_python_type(schema_name=v['schemaName'])
        self._list[i] = python_type(v['data'])

    def insert(self, i, v):
        python_type = get_python_type(schema_name=v['schemaName'])
        self._list.insert(i, python_type(v['data']))

    def __str__(self):
        return str(self._list)

    def __repr__(self):
        return str(self._list)
