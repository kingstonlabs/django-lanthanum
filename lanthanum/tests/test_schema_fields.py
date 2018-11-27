import pytest
from jsonschema.exceptions import ValidationError

from ..schema_fields import (
    Field, CharField, BooleanField, TypedField, ObjectField, OneOfArrayField
)


class TestField:
    def test_schema_basic(self):
        field = Field()
        assert field.schema == {'type': 'string', 'format': 'text'}
        assert not field._required

    def test_schema(self):
        label = "Test Field"
        default = "Thing"
        required = True
        field = Field(label=label, default=default, required=required)
        assert field.schema == {
            'type': 'string',
            'format': 'text',
            'title': label,
            'default': default
        }
        assert field._required

    def test_load_data(self):
        test_data = "A test"
        field = Field()
        field.load_data(test_data)
        assert field.data == test_data

    def test_validate(self):
        test_data = "A test"
        field = Field()
        field.load_data(test_data)
        field.validate()

    def test_validate_bad_data(self):
        test_data = {"a": "b"}
        field = Field()
        field.load_data(test_data)
        with pytest.raises(ValidationError):
            field.validate()


@pytest.fixture
def char_choices_field_options():
    return {
        'label': "Choices Field",
        'choices': (
            ("item-1", "Item 1"),
            ("item-2", "Item 2"),
            ("item-3", "Item 3")
        ),
        'default': "item-1",
        'required': True
    }


@pytest.fixture
def char_choices_field(char_choices_field_options):
    return CharField(**char_choices_field_options)


@pytest.fixture
def simple_char_field_options():
    return {
        'label': "Simple Char Field",
        'default': "Simple",
        'required': True
    }


@pytest.fixture
def simple_char_field(simple_char_field_options):
    return CharField(**simple_char_field_options)


class TestCharField:
    def test_schema_basic(self):
        field = CharField()
        assert field.schema == {'type': 'string', 'format': 'text'}
        assert not field._required

    def test_schema(self, char_choices_field_options):
        field = CharField(**char_choices_field_options)
        choices = char_choices_field_options['choices']
        assert field.schema == {
            'type': 'string',
            'format': 'text',
            'title': char_choices_field_options['label'],
            'default': char_choices_field_options['default'],
            'enumSource': [
                {
                    'source': [
                        {'value': value, 'title': label}
                        for (value, label) in choices
                    ],
                    'title': '{{item.title}}',
                    'value': '{{item.value}}'
                }
            ],
            'enum': [
                value for (value, label) in choices
            ],
            'minLength': 1
        }
        assert field._required

    def test_load_data(self, char_choices_field):
        test_data = "item-1"
        char_choices_field.load_data(test_data)
        assert char_choices_field.data == test_data

    def test_load_data_twice(self, char_choices_field):
        test_item_1 = "item-1"
        char_choices_field.load_data(test_item_1)
        test_item_2 = "item-2"
        char_choices_field.load_data(test_item_2)
        assert char_choices_field.data == test_item_2

    def test_validate(self, char_choices_field):
        test_data = "item-2"
        char_choices_field.load_data(test_data)
        char_choices_field.validate()

    def test_validate_bad_data(self, char_choices_field):
        test_data = "Invalid option"
        char_choices_field.load_data(test_data)
        with pytest.raises(ValidationError):
            char_choices_field.validate()


@pytest.fixture
def simple_boolean_field_options():
    return {
        'label': "Simple Bool Field",
        'default': True,
        'required': True
    }


@pytest.fixture
def simple_boolean_field(simple_boolean_field_options):
    return BooleanField(**simple_boolean_field_options)


class TestBooleanField:
    def test_schema_basic(self):
        field = BooleanField()
        assert field.schema == {'type': 'boolean', 'format': 'checkbox'}
        assert not field._required

    def test_schema(self, simple_boolean_field_options):
        field = BooleanField(**simple_boolean_field_options)
        assert field.schema == {
            'type': 'boolean',
            'format': 'checkbox',
            'title': simple_boolean_field_options['label'],
            'default': simple_boolean_field_options['default']
        }
        assert field._required

    def test_load_data(self, simple_boolean_field):
        test_data = False
        simple_boolean_field.load_data(test_data)
        assert simple_boolean_field.data == test_data

    def test_load_data_converts_strings(self, simple_boolean_field):
        test_data = "False"
        simple_boolean_field.load_data(test_data)
        assert simple_boolean_field.data is False
        test_data = "True"
        simple_boolean_field.load_data(test_data)
        assert simple_boolean_field.data is True
        test_data = "false"
        simple_boolean_field.load_data(test_data)
        assert simple_boolean_field.data is False
        test_data = "true"
        simple_boolean_field.load_data(test_data)
        assert simple_boolean_field.data is True

    def test_validate(self, simple_boolean_field):
        test_data = True
        simple_boolean_field.load_data(test_data)
        simple_boolean_field.validate()

    def test_validate_bad_data(self, simple_boolean_field):
        test_data = "Non-boolean"
        simple_boolean_field.load_data(test_data)
        with pytest.raises(ValidationError):
            simple_boolean_field.validate()


@pytest.fixture
def typed_char_field(simple_char_field):
    return TypedField(field=simple_char_field, schema_type="simple_field")


class TestTypedField:
    def test_schema(self, simple_char_field_options):
        schema_type = "simple_field"
        base_field = CharField(**simple_char_field_options)
        field = TypedField(field=base_field, schema_type=schema_type)
        assert field.schema == {
            'type': 'object',
            'title': simple_char_field_options['label'],
            'properties': {
                'schemaType': {
                    'title': 'Schema Type',
                    'const': schema_type,
                    'type': 'string',
                    'default': schema_type,
                    'template': schema_type
                },
                'data': {
                    'type': 'string',
                    'format': 'text',
                    'title': simple_char_field_options['label'],
                    'default': simple_char_field_options['default'],
                    'minLength': 1
                }
            },
            "defaultProperties": ["data", "schemaType"],
            "required": ['data', 'schemaType']
        }
        assert field._required

    def test_load_data(self, typed_char_field):
        test_data = {
            "schemaType": "simple_field",
            "data": "Test Content"
        }
        typed_char_field.load_data(test_data)
        assert typed_char_field.data == test_data
        assert str(typed_char_field) == test_data['data']

    def test_load_data_twice(self, typed_char_field):
        test_item_1 = {
            "schemaType": "simple_field_a",
            "data": "Test Content 1"
        }
        test_item_2 = {
            "schemaType": "simple_field_b",
            "data": "Test Content 2"
        }
        typed_char_field.load_data(test_item_1)
        typed_char_field.load_data(test_item_2)
        assert typed_char_field.data == test_item_2
        assert str(typed_char_field) == test_item_2['data']


@pytest.fixture
def dog_field():
    class DogField(ObjectField):
        name = CharField(required=True)
        breed = CharField()
    return DogField()


@pytest.fixture
def dog_schema():
    return {
        'type': 'object',
        'properties': {
            'name': {
                'title': 'Name',
                'type': 'string',
                'format': 'text',
                'minLength': 1
            },
            'breed': {
                'title': 'Breed',
                'type': 'string',
                'format': 'text'
            }
        },
        'required': ['name']
    }


@pytest.fixture
def cat_schema():
    return {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "format": "text",
                "title": "Name",
                "minLength": 1
            },
            "scratches": {
                "type": "boolean",
                "format": "checkbox",
                "title": "Scratches",
                "default": True
            }
        },
        "required": ["name", "scratches"]
    }


@pytest.fixture
def cat_field():
    class CatField(ObjectField):
        name = CharField(required=True)
        scratches = BooleanField(required=True, default=True)
    return CatField()


class TestObjectField:
    def test_schema(self, dog_field, dog_schema):
        assert dog_field.schema == dog_schema

    def test_load_data(self, dog_field):
        scooby_doo = {'name': 'Scooby Doo', 'breed': 'Daschund'}
        dog_field.load_data(scooby_doo)
        assert dog_field.data == scooby_doo
        assert str(dog_field.name) == scooby_doo['name']
        assert str(dog_field.breed) == scooby_doo['breed']

    def test_load_data_twice(self, dog_field):
        scooby_doo = {'name': 'Scooby Doo', 'breed': 'Daschund'}
        snoopy = {'name': 'Snoopy', 'breed': 'beagle'}
        dog_field.load_data(scooby_doo)
        dog_field.load_data(snoopy)
        assert dog_field.data == snoopy
        assert str(dog_field.name) == snoopy['name']
        assert str(dog_field.breed) == snoopy['breed']


@pytest.fixture
def pet_list_field_options():
    return {
        'label': "Pets",
        'required': True,
        'item_label': "Pet",
        "max_items": 10,
        "min_items": 2
    }


@pytest.fixture
def pet_list_field(dog_field, cat_field, pet_list_field_options):
    class AnimalListField(OneOfArrayField):
        dog = dog_field
        cat = cat_field
    return AnimalListField(**pet_list_field_options)


class TestOneOfArrayField:
    def test_schema(self, pet_list_field, dog_schema, cat_schema):
        labeled_dog_schema = dog_schema.copy()
        labeled_dog_schema['title'] = 'Dog'
        labeled_cat_schema = cat_schema.copy()
        labeled_cat_schema['title'] = 'Cat'

        expected_schema = {
            "type": "array",
            "format": "tabs",
            "title": "Pets",
            "items": {
                "title": "Pet",
                "headerTemplate": "Pet {{i1}}.",
                "oneOf": [
                    {
                        "type": "object",
                        "title": "Dog",
                        "properties": {
                            "schemaType": {
                                "title": "Schema Type",
                                "const": "dog",
                                "type": "string",
                                "default": "dog",
                                "template": "dog"
                            },
                            "data": labeled_dog_schema
                        },
                        "defaultProperties": ["data", "schemaType"],
                        "required": ["data", "schemaType"]
                    },
                    {
                        "type": "object",
                        "title": "Cat",
                        "properties": {
                            "schemaType": {
                                "title": "Schema Type",
                                "const": "cat",
                                "type": "string",
                                "default": "cat",
                                "template": "cat"
                            },
                            "data": labeled_cat_schema
                        },
                        "defaultProperties": ["data", "schemaType"],
                        "required": ["data", "schemaType"]
                    }
                ]
            },
            "minItems": 2,
            "maxItems": 10
        }
        assert pet_list_field.schema == expected_schema

    def test_load_single_item(self, pet_list_field):
        items = [
            {
                'schemaType': 'dog',
                'data': {'name': 'Scooby Doo', 'breed': 'Daschund'}
            }
        ]
        pet_list_field.load_data(items)
        assert len(pet_list_field) == 1
        pet = pet_list_field[0]
        assert str(pet.name) == items[0]['data']['name']
        assert str(pet.breed) == items[0]['data']['breed']
        assert pet.schema_type == items[0]['schemaType']

    def test_load_single_item_twice(self, pet_list_field):
        items_a = [
            {
                'schemaType': 'dog',
                'data': {'name': 'Scooby Doo', 'breed': 'Daschund'}
            }
        ]
        items_b = [
            {
                'schemaType': 'cat',
                'data': {'name': 'Top Cat', 'scratches': True}
            }
        ]
        pet_list_field.load_data(items_a)
        pet_list_field.load_data(items_b)

        assert len(pet_list_field) == 1
        pet = pet_list_field[0]
        assert str(pet.name) == items_b[0]['data']['name']
        assert bool(pet.scratches) == items_b[0]['data']['scratches']
        assert pet.schema_type == items_b[0]['schemaType']

    def test_load_multiple_items(self, pet_list_field):
        items = [
            {
                'schemaType': 'dog',
                'data': {'name': 'Scooby Doo', 'breed': 'Daschund'}
            },
            {
                'schemaType': 'cat',
                'data': {'name': 'Top Cat', 'scratches': True}
            }
        ]
        pet_list_field.load_data(items)

        assert len(pet_list_field) == 2

        for i in range(2):
            assert (
                pet_list_field[i].schema_type == items[i]['schemaType']
            )
            pet_data = items[i]['data']
            assert pet_list_field[i].data['data'] == pet_data
            for key, value in pet_data.items():
                assert str(getattr(pet_list_field[i], key)) == str(value)
