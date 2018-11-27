import copy
import logging

from django.conf import settings
from jsonschema import validate


logger = logging.getLogger(__name__)


class Field(object):
    class Meta:
        data_type = 'string'
        data_format = 'text'

    def __init__(self, **kwargs):
        self._label = (
            kwargs.get('label') or getattr(self.Meta, 'label', None)
        )
        self._default = (
            kwargs.get('default') or getattr(self.Meta, 'default', None)
        )
        self._required = kwargs.get('required', False)
        self.data = None

    def __str__(self):
        return format(self.data)

    def __bool__(self):
        return bool(self.data)

    @property
    def schema(self):
        schema = {}
        if self.Meta.data_type is not None:
            schema['type'] = self.Meta.data_type
        if self.Meta.data_format is not None:
            schema['format'] = self.Meta.data_format
        if self._label is not None:
            schema['title'] = self._label
        if self._default is not None:
            schema['default'] = self._default
        return schema

    def load_data(self, data):
        self.data = data

    def validate(self):
        validate(self.data, self.schema)


class CharField(Field):
    class Meta:
        data_type = 'string'
        data_format = 'text'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._choices = kwargs.pop("choices", None)
        self._min_length = kwargs.pop("min_length", None)
        self._max_length = kwargs.pop("max_length", None)

    @property
    def schema(self):
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

    def load_data(self, data):
        self.data = data or ""


class TextField(Field):
    class Meta:
        data_type = 'string'
        data_format = 'textarea'

    @property
    def schema(self):
        schema = super().schema
        if self._required:
            schema['minLength'] = 1
        return schema

    def load_data(self, data):
        self.data = data or ""


class BooleanField(Field):
    class Meta:
        data_type = 'boolean'
        data_format = 'checkbox'

    def load_data(self, data):
        if data in ["true", "True"]:
            data = True
        elif data in ["false", "False"]:
            data = False

        self.data = data


class IntegerField(Field):
    class Meta:
        data_type = 'integer'
        data_format = 'number'


class DecimalField(Field):
    class Meta:
        data_type = 'number'
        data_format = 'number'


class ObjectField(Field):
    class Meta:
        data_type = 'object'
        data_format = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make a copy of each field for this instance, so we can load data
        # into them without affecting other instances
        self._sub_fields = {}
        for name, field in self.__class__.__dict__.items():
            if isinstance(field, Field):
                instance_field = copy.deepcopy(field)
                setattr(self, name, instance_field)
                self._sub_fields[name] = instance_field

    def _get_required(self):
        sub_fields = self._sub_fields
        return [
            field_name for field_name, field in sub_fields.items()
            if field._required
        ]

    @property
    def schema(self):
        schema = super().schema
        schema['properties'] = {}
        for name, sub_field in self._sub_fields.items():
            sub_field._label = name.title().replace("_", " ")
            schema['properties'][name] = sub_field.schema
        schema['required'] = self._get_required()
        return schema

    def load_data(self, data):
        if data is None:
            self.data = None
            return
        if not isinstance(data, dict):
            logger.warning(
                "ObjectField data was not a dictionary - it was `{}`".format(
                    data
                )
            )
            self.data = data
            return
        self.data = {}
        for name, field in self._sub_fields.items():
            field.load_data(data=data.get(name))
            self.data[name] = field.data


class FilePathField(Field):
    class Meta:
        data_type = 'string'
        data_format = 'text'

    def __init__(self, *args, **kwargs):
        self._media_type = kwargs.get('media_type')
        super().__init__(**kwargs)

    @property
    def schema(self):
        schema = super().schema
        if self._required:
            schema['minLength'] = 1

        media_link = {
            "href": "{}{{{{self}}}}".format(settings.MEDIA_URL)
        }
        if self._media_type is not None:
            media_link['mediaType'] = self._media_type

        schema["links"] = [media_link]

        return schema

    def load_data(self, data):
        self.data = data or ""


class TypedField(Field):
    """
    Like a field, but includes meta data about what schema type it is.

    This is useful for validating OneOf Schemas because it includes the schema
    type as a constant.
    """
    def __init__(self, field, schema_type):
        self._field = copy.deepcopy(field)
        if self._field._label is None:
            self._field._label = schema_type.title().replace("_", " ")
        self.schema_type = schema_type

    def __getattr__(self, name):
        if name.startswith("__"):
            # Don't change special methods
            return super().__getattr__(name)
        else:
            return getattr(self._field, name)

    def __str__(self):
        return str(self._field)

    @property
    def schema(self):
        schema = {
            'type': 'object',
            'title': self._field._label,
            'properties': {
                'schemaType': {
                    'title': 'Schema Type',
                    'const': self.schema_type,
                    'type': 'string',
                    'default': self.schema_type,
                    # JSON Editor isn't very good at making a const field, so
                    # set to a static template
                    'template': self.schema_type
                },
                'data': self._field.schema
            },
            "defaultProperties": ["data", "schemaType"],
            "required": ['data', 'schemaType']
        }
        return schema

    def load_data(self, data):
        self.data = data
        self.data['schemaType'] = self.schema_type
        self._field.load_data(data.get("data"))


class OneOfArray(list):
    def __init__(self, **fields):
        super().__init__()


class OneOfArrayField(Field, OneOfArray):
    class Meta:
        data_type = 'array'
        data_format = 'tabs'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._unique_items = kwargs.get("unique_items")
        self._max_items = kwargs.get("max_items")
        self._min_items = kwargs.get("min_items")
        self._item_label = kwargs.get("item_label", "Item")

        self._allowed_fields = {}
        for name, field in self.__class__.__dict__.items():
            if isinstance(field, Field):
                self._allowed_fields[name] = TypedField(
                    field=field, schema_type=name
                )

    @property
    def schema(self):
        schema = super().schema

        schema['items'] = {
            'title': self._item_label,
            'headerTemplate': "{} {{{{i1}}}}.".format(self._item_label),
            'oneOf': [
                field.schema
                for field in self._allowed_fields.values()
            ]
        }

        if self._unique_items is not None:
            schema['uniqueItems'] = self._unique_items
        if self._min_items is not None:
            schema['minItems'] = self._min_items
        if self._max_items is not None:
            schema['maxItems'] = self._max_items
        return schema

    def load_data(self, data):
        self.data = data

        del self[:]

        for data_item in data:
            schema_type = data_item.get('schemaType')
            base_field = self._allowed_fields.get(schema_type)
            if base_field is None:
                continue
            field = copy.deepcopy(base_field)
            field.load_data(data_item)
            self.append(field)
