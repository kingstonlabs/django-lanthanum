from decimal import Decimal

from ..schema_fields import (
    ArrayField,
    BooleanField,
    DynamicArrayField,
    Field,
    CharField,
    DecimalField,
    IntegerField,
    TextField
)
from .utils import assert_dict_equal


class TestField:
    def test_schema_basic(self):
        field = Field()
        assert field.schema == {'type': 'string', 'format': 'text'}

    def test_schema(self):
        label = "Test Field"
        default = "Thing"
        required = True
        field = Field(label=label, default=default, required=required)
        assert_dict_equal(
            expected={
                'type': 'string',
                'format': 'text',
                'title': label,
                'default': default
            },
            actual=field.schema
        )

    def test_load_data(self):
        test_data = "A test"
        field = Field()
        loaded_data = field.Meta.python_type(test_data)
        assert loaded_data == test_data


class TestCharField:
    def test_schema_basic(self):
        field = CharField()
        assert field.schema == {'type': 'string', 'format': 'text'}

    def test_schema(self):
        label = "Test Field"
        default = "Thing"
        required = True
        field = CharField(label=label, default=default, required=required)
        assert_dict_equal(
            expected={
                'type': 'string',
                'format': 'text',
                'minLength': 1,
                'title': label,
                'default': default
            },
            actual=field.schema
        )

    def test_schema_min_max_length(self):
        label = "Test Field"
        default = "Thing"
        required = True
        min_length = 3
        max_length = 5
        field = CharField(
            label=label,
            default=default,
            required=required,
            min_length=min_length,
            max_length=max_length
        )
        assert_dict_equal(
            expected={
                'type': 'string',
                'format': 'text',
                'minLength': min_length,
                'maxLength': max_length,
                'title': label,
                'default': default
            },
            actual=field.schema
        )

    def test_schema_choices(self):
        label = "Test Field"
        default = "cat"
        choices = [('cat', 'Cat'), ('dog', 'Dog'), ('fish', 'Fish')]
        required = True
        field = CharField(
            label=label,
            choices=choices,
            default=default,
            required=required
        )
        assert_dict_equal(
            expected={
                'type': 'string',
                'format': 'text',
                'minLength': 1,
                'title': label,
                'default': default,
                'enum': ['cat', 'dog', 'fish'],
                'enumSource': [
                    {
                        'source': [
                            {'value': choice_value, 'title': choice_label}
                            for (choice_value, choice_label) in choices
                        ],
                        'title': '{{item.title}}',
                        'value': '{{item.value}}'
                    }
                ],
            },
            actual=field.schema
        )

    def test_load_data(self):
        test_data = "A test"
        field = CharField()
        loaded_data = field.Meta.python_type(test_data)
        assert loaded_data == test_data


class TestTextField:
    def test_schema_basic(self):
        field = TextField()
        assert_dict_equal(
            expected={'type': 'string', 'format': 'textarea'},
            actual=field.schema
        )

    def test_schema(self):
        label = "Test Field"
        default = "Thing"
        required = True
        field = TextField(label=label, default=default, required=required)
        assert_dict_equal(
            expected={
                'type': 'string',
                'format': 'textarea',
                'minLength': 1,
                'title': label,
                'default': default
            },
            actual=field.schema
        )

    def test_load_data(self):
        test_data = "A test"
        field = TextField()
        loaded_data = field.Meta.python_type(test_data)
        assert loaded_data == test_data


class TestIntegerField:
    def test_schema_basic(self):
        field = IntegerField()
        assert_dict_equal(
            expected={'type': 'integer', 'format': 'number'},
            actual=field.schema
        )

    def test_schema(self):
        label = "Test Field"
        default = 5
        required = True
        field = IntegerField(label=label, default=default, required=required)
        assert_dict_equal(
            expected={
                'type': 'integer',
                'format': 'number',
                'title': label,
                'default': default
            },
            actual=field.schema
        )

    def test_load_data(self):
        test_data = 8
        field = IntegerField()
        loaded_data = field.Meta.python_type(test_data)
        assert loaded_data == test_data


class TestDecimalField:
    def test_schema_basic(self):
        field = DecimalField()
        assert_dict_equal(
            expected={'type': 'decimal', 'format': 'number'},
            actual=field.schema
        )

    def test_schema(self):
        label = "Test Field"
        default = Decimal('5.5')
        required = True
        field = DecimalField(label=label, default=default, required=required)
        assert_dict_equal(
            expected={
                'type': 'decimal',
                'format': 'number',
                'title': label,
                'default': default
            },
            actual=field.schema
        )

    def test_load_data(self):
        test_data = Decimal('3.14')
        field = DecimalField()
        loaded_data = field.Meta.python_type(test_data)
        assert loaded_data == test_data


class TestBooleanField:
    def test_schema_basic(self):
        field = BooleanField()
        assert_dict_equal(
            expected={'type': 'boolean', 'format': 'checkbox'},
            actual=field.schema
        )

    def test_schema(self):
        label = "Test Field"
        default = False
        required = True
        field = BooleanField(label=label, default=default, required=required)
        assert_dict_equal(
            expected={
                'type': 'boolean',
                'format': 'checkbox',
                'title': label,
                'default': default
            },
            actual=field.schema
        )

    def test_load_data(self):
        test_data = True
        field = BooleanField()
        loaded_data = field.Meta.python_type(test_data)
        assert loaded_data == test_data


class TestObjectField:
    def test_schema(self, dog_field, dog_schema):
        assert_dict_equal(
            expected=dog_schema,
            actual=dog_field().schema
        )

    def test_typed_schema(self, dog_field, typed_dog_schema):
        assert_dict_equal(
            expected=typed_dog_schema,
            actual=dog_field().typed_schema
        )

    def test_load_data(self, dog_field, scooby_doo):
        loaded_data = dog_field().Meta.python_type(scooby_doo)
        assert loaded_data.name == scooby_doo['name']
        assert loaded_data.breed == scooby_doo['breed']

    def test_nested_schema(self, person_field, person_schema):
        assert_dict_equal(expected=person_schema, actual=person_field().schema)

    def test_load_nested_data(self, person_field, scooby_doo, shaggy):
        loaded_data = person_field().Meta.python_type(shaggy)
        assert loaded_data.name == shaggy['name']
        assert loaded_data.favourite_dog.name == scooby_doo['name']
        assert loaded_data.favourite_dog.breed == scooby_doo['breed']

    def test_instances_copy_methods(self, dog_field, scooby_doo):
        """
        Methods declared on the field should be available to the instance
        """
        loaded_data = dog_field().Meta.python_type(scooby_doo)
        assert loaded_data.name == scooby_doo['name']
        assert loaded_data.short_name == scooby_doo['name'][:3]


class TestSubClassedObjectField:
    def test_schema(self, parrot_field, parrot_schema):
        assert_dict_equal(
            expected=parrot_schema,
            actual=parrot_field().schema
        )

    def test_typed_schema(self, parrot_field, typed_parrot_schema):
        assert_dict_equal(
            expected=typed_parrot_schema,
            actual=parrot_field().typed_schema
        )

    def test_load_data(self, parrot_field):
        polly = {'name': 'Polly', 'talks': True}
        loaded_data = parrot_field().Meta.python_type(polly)
        assert loaded_data.name == polly['name']
        assert loaded_data.talks == polly['talks']

    def test_instances_copy_parent_methods(self, parrot_field):
        """
        Methods declared on the parent field should be copied to the instance
        """
        polly = {'name': 'Polly', 'talks': True}
        loaded_data = parrot_field().Meta.python_type(polly)
        assert loaded_data.loud_name == polly['name'].upper()


class TestArrayField:
    def test_schema(self, dog_field, dog_schema):
        dog_list_field = ArrayField(base_field=dog_field())
        assert_dict_equal(
            expected={
                'type': 'array',
                'format': 'table',
                'title': 'Dog List',
                'items': dog_schema
            },
            actual=dog_list_field.schema
        )

    def test_load_data(self, dog_field, scooby_doo, snoopy):
        dog_list_field = ArrayField(base_field=dog_field())

        dog_list = [scooby_doo, snoopy]

        loaded_data = dog_list_field.Meta.python_type(dog_list)
        assert len(loaded_data) == 2
        scooby_doo_instance = loaded_data[0]
        snoopy_instance = loaded_data[1]
        assert scooby_doo_instance.name == scooby_doo['name']
        assert scooby_doo_instance.breed == scooby_doo['breed']
        assert snoopy_instance.name == snoopy['name']
        assert snoopy_instance.breed == snoopy['breed']


class TestDynamicArrayField:
    def test_schema(
        self, dog_field, fish_field, typed_dog_schema, typed_fish_schema
    ):
        item_label = "Pet"
        schema_name = "pet_list"
        unique_items = True
        min_items = 2
        max_items = 5

        pet_field = DynamicArrayField(
            schema_name=schema_name,
            item_label=item_label,
            allowed_fields=[dog_field(), fish_field()],
            unique_items=unique_items,
            min_items=min_items,
            max_items=max_items
        )
        assert_dict_equal(
            expected={
                'type': 'array',
                'format': 'tabs',
                'title': schema_name.replace("_", " ").title(),
                'uniqueItems': unique_items,
                'minItems': min_items,
                'maxItems': max_items,
                'items': {
                    'headerTemplate': "{} {{{{i1}}}}.".format(item_label),
                    'oneOf': [typed_dog_schema, typed_fish_schema],
                    'title': item_label
                }
            },
            actual=pet_field.schema
        )

    def test_auto_generated_schema_name(
        self, dog_field, fish_field, typed_dog_schema, typed_fish_schema
    ):
        """
        If no schema name is provided, it should be built from allowed fields
        """
        item_label = "Pet"
        pet_field = DynamicArrayField(
            item_label=item_label,
            allowed_fields=[dog_field(), fish_field()]
        )
        assert pet_field.Meta.schema_name == "one_of_dog_or_fish"
        assert pet_field.schema['title'] == "One Of Dog Or Fish"

    def test_provided_schema_name(
        self, dog_field, fish_field, typed_dog_schema, typed_fish_schema
    ):
        """
        If a schema name is provided, it should be available as class meta
        """
        item_label = "Pet"
        pet_field = DynamicArrayField(
            item_label=item_label,
            schema_name="pet",
            allowed_fields=[dog_field(), fish_field()]
        )
        assert pet_field.Meta.schema_name == "pet"

    def test_load_data(
        self,
        dog_field,
        fish_field,
        typed_dog_schema,
        typed_fish_schema,
        scooby_doo,
        nemo
    ):
        item_label = "Pet"
        pet_field = DynamicArrayField(
            item_label=item_label,
            allowed_fields=[dog_field(), fish_field()]
        )

        pet_list = [
            {
                "schemaName": "dog",
                "data": scooby_doo
            },
            {
                "schemaName": "fish",
                "data": nemo
            }
        ]

        loaded_data = pet_field.Meta.python_type(pet_list)
        assert len(loaded_data) == 2
        scooby_doo_instance = loaded_data[0]
        nemo_instance = loaded_data[1]
        assert scooby_doo_instance.name == scooby_doo['name']
        assert scooby_doo_instance.breed == scooby_doo['breed']
        assert nemo_instance.name == nemo['name']
        assert nemo_instance.salt_water == nemo['salt_water']
