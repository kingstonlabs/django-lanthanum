from decimal import Decimal
import logging

from .field_types import DynamicArray, DynamicObject, TypedArray
from .schema_registry import schema_registry
from .utils import field_to_schema_name


logger = logging.getLogger(__name__)


class Field(object):
    """
    Basic JSON schema field definition
    """
    class Meta:
        python_type = str
        schema_type = 'string'
        schema_format = 'text'
        schema_name = 'field'
        abstract = True

        @classmethod
        def get_default_label(cls):
            return None

    def __new__(cls, *args, **kwargs):
        """
        Configure the new field
        """
        new_class = super().__new__(cls)

        # Inherit meta attributes from base classes
        merged_meta_dict = {}
        for base in reversed(cls.mro()):
            if hasattr(base, 'Meta'):
                merged_meta_dict.update(base.Meta.__dict__)
        # Abstract should always default to False unless explicitly specified
        # Schema name should not be inherited
        merged_meta_dict.update({
            'abstract': getattr(new_class.Meta, 'abstract', False),
            'schema_name': (
                getattr(new_class.Meta, 'schema_name', None) or
                field_to_schema_name(new_class.__class__.__name__)
            )
        })

        new_class.Meta = type('Meta', (), merged_meta_dict)

        key = new_class.Meta.schema_name

        is_abstract = getattr(cls.Meta, 'abstract', False)
        if not is_abstract and key not in schema_registry:
            schema_registry[key] = new_class
        return new_class

    def __init__(self, **kwargs):
        """
        Configure options: label, default and required
        """
        self._label = kwargs.get('label', self.Meta.get_default_label())
        self._default = kwargs.get('default')
        self._required = kwargs.get('required', False)

    @property
    def schema(self):
        """
        The JSON Schema for basic fields
        """
        schema = {}
        if self.Meta.schema_type is not None:
            schema['type'] = self.Meta.schema_type
        if self.Meta.schema_format is not None:
            schema['format'] = self.Meta.schema_format
        if self._label is not None:
            schema['title'] = self._label
        if self._default is not None:
            schema['default'] = self._default
        return schema

    @property
    def typed_schema(self):
        """
        Add data typing to the schema by wrapping it with metadata

        This is useful for validating OneOf Schemas because it includes the
        schema type as a constant.
        """
        schema = {
            'type': 'object',
            'properties': {
                'schemaName': {
                    'title': 'Schema Name',
                    'const': self.Meta.schema_name,
                    'type': 'string',
                    'default': self.Meta.schema_name,
                    # JSON Editor isn't very good at making a const field, so
                    # set to a static template
                    'template': self.Meta.schema_name
                },
                'data': self.schema
            },
            "defaultProperties": ["data", "schemaName"],
            "required": ['data', 'schemaName']
        }
        if self._label is not None:
            schema['title'] = self._label
        return schema


class CharField(Field):
    """
    JSON Schema Field for a simple string input
    """
    class Meta:
        python_type = str
        schema_type = 'string'
        schema_format = 'text'
        schema_name = 'charfield'
        abstract = False

    def __init__(self, **kwargs):
        """
        Configure with choices, min_length and max_length options
        """
        super().__init__(**kwargs)
        self._choices = kwargs.pop("choices", None)
        self._min_length = kwargs.pop("min_length", None)
        self._max_length = kwargs.pop("max_length", None)

    @property
    def schema(self):
        """
        CharField schema including choices and min / max length
        """
        schema = super().schema
        if self._choices:
            schema['enumSource'] = [
                {
                    'source': [
                        {'value': value, 'title': label}
                        for (value, label) in self._choices
                    ],
                    'title': '{{item.title}}',
                    'value': '{{item.value}}'
                }
            ]
            schema['enum'] = [value for (value, label) in self._choices]
        if self._required and self._min_length is None:
            schema['minLength'] = 1
        if self._min_length:
            schema['minLength'] = self._min_length
        if self._max_length:
            schema['maxLength'] = self._max_length
        return schema


class TextField(Field):
    """
    JSON Schema field for larger text inputs
    """
    class Meta:
        python_type = str
        schema_type = 'string'
        schema_format = 'textarea'
        schema_name = 'textfield'
        abstract = False

    @property
    def schema(self):
        """
        Just set min length for required fields
        """
        schema = super().schema
        if self._required:
            schema['minLength'] = 1
        return schema


class BooleanField(Field):
    """
    JSON Schema for boolean inputs
    """
    class Meta:
        python_type = bool
        schema_type = 'boolean'
        schema_format = 'checkbox'
        schema_name = 'booleanfield'
        abstract = False


class IntegerField(Field):
    """
    JSON Schema for integer inputs
    """
    class Meta:
        python_type = int
        schema_type = 'integer'
        schema_format = 'number'
        schema_name = 'integerfield'
        abstract = False


class DecimalField(Field):
    """
    JSON Schema for decimal inputs
    """
    class Meta:
        python_type = Decimal
        schema_type = 'decimal'
        schema_format = 'number'
        schema_name = 'numberfield'
        abstract = False


class ObjectField(Field):
    """
    JSON Schema for object inputs
    """
    class Meta:
        python_type = DynamicObject
        schema_type = 'object'
        schema_format = None
        schema_name = None
        abstract = True

        @classmethod
        def get_default_label(cls):
            return cls.schema_name.replace("_", " ").title()

    def __new__(cls, *args, **kwargs):
        """
        Configure the new field with the sub fields specified

        This dynamically generates a new python type to fit the JSON Schema.
        """
        schema_name = (
            cls.Meta.schema_name or
            field_to_schema_name(cls.__name__)
        )

        if schema_name in schema_registry:
            return schema_registry[schema_name]

        new_class = super().__new__(cls, *args, **kwargs)

        sub_fields = {}
        python_type_dict = {}
        for base in reversed(cls.mro()):
            sub_fields.update({
                name: field
                for name, field in base.__dict__.items()
                if isinstance(field, Field)
            })
            python_type_dict.update({
                name: prop
                for name, prop in base.__dict__.items()
                if not name.startswith("__")
            })

        new_class._sub_fields = sub_fields
        new_class._required_field_names = [
            name for name, field in new_class._sub_fields.items()
            if field._required
        ]

        python_type_dict.update({
            key: field.Meta.python_type
            for key, field in new_class._sub_fields.items()
        })
        # Make sure the schema name is available to the resulting type
        python_type_dict['schema_name'] = schema_name

        python_type = type(
            "{}Type".format(cls.__name__.rstrip("Field")),
            (DynamicObject,),
            python_type_dict
        )

        # Inherit meta attributes from base classes
        merged_meta_dict = {}
        for base in reversed(cls.mro()):
            if hasattr(base, 'Meta'):
                merged_meta_dict.update(base.Meta.__dict__)
        merged_meta_dict.update({
            'python_type': python_type,
            'schema_name': schema_name,
            'schema_type': 'object',
            'schema_format': None,
            'abstract': False
        })

        new_class.Meta = type('Meta', (), merged_meta_dict)

        schema_registry[schema_name] = new_class
        return new_class

    @property
    def schema(self):
        """
        Build the schema by iterating over each of the sub fields.
        """
        schema = super().schema
        schema['properties'] = {}
        for name, sub_field in self._sub_fields.items():
            sub_field_schema = sub_field.schema.copy()
            sub_field_schema['title'] = name.title().replace("_", " ")
            schema['properties'][name] = sub_field_schema
        schema['required'] = self._required_field_names
        return schema


class ArrayField(Field):
    """
    JSON Schema for simple array inputs
    """
    class Meta:
        python_type = TypedArray
        schema_type = 'array'
        schema_format = 'table'
        schema_name = None
        abstract = True

        @classmethod
        def get_default_label(cls):
            simple_label = cls.schema_name.rstrip("_array")
            return "{} List".format(simple_label.replace("_", " ").title())

    def __new__(cls, *args, **kwargs):
        """
        Configure the new field with the base field specified

        This dynamically generates a python array type to contain each item.
        """
        base_field = kwargs.pop('base_field', Field)

        schema_name = cls.Meta.schema_name or "{}_array".format(
            base_field.Meta.schema_name
        )
        if schema_name in schema_registry:
            return schema_registry[schema_name]

        new_class = super().__new__(cls, *args, **kwargs)
        new_class._base_field = base_field

        array_type_meta = type(
            'Meta',
            (),
            {'base_type': base_field.Meta.python_type}
        )
        python_type = type(
            "{}ArrayType".format(
                base_field.__class__.__name__.rstrip("Field")
            ),
            (TypedArray,),
            {'Meta': array_type_meta}
        )

        # Inherit meta attributes from base classes
        merged_meta_dict = {}
        for base in reversed(cls.mro()):
            if hasattr(base, 'Meta'):
                merged_meta_dict.update(base.Meta.__dict__)
        merged_meta_dict.update({
            'python_type': python_type,
            'schema_name': schema_name,
            'schema_type': 'array',
            'schema_format': 'table',
            'abstract': False
        })
        new_class.Meta = type('Meta', (), merged_meta_dict)

        schema_registry[schema_name] = new_class
        return new_class

    @property
    def schema(self):
        """
        Build the schema by iterating over each of the sub fields.
        """
        schema = super().schema
        schema['items'] = self._base_field.schema
        return schema


class DynamicArrayField(Field):
    """
    An array of items that may be of different types

    This stores the typed schema for each item so that it can be processed
    properly when converted into python.
    """
    class Meta:
        python_type = DynamicArray
        schema_type = 'array'
        schema_format = 'tabs'
        schema_name = None
        abstract = False

        @classmethod
        def get_default_label(cls):
            return cls.schema_name.replace("_", " ").title()

    def __new__(cls, *args, **kwargs):
        """
        Configure the new field with the allowed fields specified

        This generates a dynamic python array type to contain each item.
        """
        allowed_fields = kwargs.pop('allowed_fields')
        schema_name = (
            kwargs.pop('schema_name', None) or
            "one_of_{}".format("_or_".join([
                field.Meta.schema_name
                for field in allowed_fields
            ]))
        )

        if schema_name in schema_registry:
            return schema_registry[schema_name]

        new_class = super().__new__(cls, *args, **kwargs)
        new_class._allowed_fields = allowed_fields

        # Inherit meta attributes from base classes
        merged_meta_dict = {}
        for base in reversed(cls.mro()):
            if hasattr(base, 'Meta'):
                merged_meta_dict.update(base.Meta.__dict__)
        merged_meta_dict.update({
                'python_type': cls.Meta.python_type,
                'schema_name': schema_name,
                'schema_type': 'array',
                'schema_format': 'tabs',
                'abstract': False
            })
        new_class.Meta = type('Meta', (), merged_meta_dict)

        schema_registry[schema_name] = new_class
        return new_class

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._unique_items = kwargs.get("unique_items")
        self._max_items = kwargs.get("max_items")
        self._min_items = kwargs.get("min_items")
        self._item_label = kwargs.get("item_label", "Item")

    @property
    def schema(self):
        schema = super().schema

        schema['items'] = {
            'title': self._item_label,
            'headerTemplate': "{} {{{{i1}}}}.".format(self._item_label),
            'oneOf': [field.typed_schema for field in self._allowed_fields]
        }

        if self._unique_items is not None:
            schema['uniqueItems'] = self._unique_items
        if self._min_items is not None:
            schema['minItems'] = self._min_items
        if self._max_items is not None:
            schema['maxItems'] = self._max_items
        return schema
