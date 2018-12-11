from collections import MutableSequence

from .schema_registry import get_python_type


class DynamicObject(object):
    """
    A type for schema objects to subclass
    """
    @classmethod
    def _get_sub_types(cls):
        return {
            name: field_type
            for name, field_type in cls.__dict__.items()
        }

    def __init__(self, data):
        self._data = data
        sub_types = self._get_sub_types()
        for k, v in data.items():
            if k in sub_types:
                setattr(self, k, sub_types[k](v))


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
