from django.forms import ModelForm
import pytest

from ..schema_fields import BooleanField, CharField, ObjectField
from .mock_app.models import RecordShop


@pytest.fixture
def scooby_doo():
    return {'name': 'Scooby Doo', 'breed': 'Daschund'}


@pytest.fixture
def snoopy():
    return {'name': 'Snoopy', 'breed': 'Beagle'}


@pytest.fixture
def shaggy(scooby_doo):
    return {'name': 'Shaggy', 'favourite_dog': scooby_doo}


@pytest.fixture
def nemo():
    return {'name': 'Nemo', 'salt_water': True}


@pytest.fixture
def dog_field():
    class DogField(ObjectField):
        name = CharField(required=True)
        breed = CharField()

        @property
        def short_name(self):
            return self.name[:3]

    return DogField


@pytest.fixture
def dog_schema():
    return {
        'type': 'object',
        'title': 'Dog',
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
def typed_dog_schema(dog_schema):
    schema_name = 'dog'
    return {
        'type': 'object',
        'title': 'Dog',
        'properties': {
            'schemaName': {
                'title': 'Schema Name',
                'const': schema_name,
                'type': 'string',
                'default': schema_name,
                'template': schema_name
            },
            'data': dog_schema
        },
        "defaultProperties": ["data", "schemaName"],
        "required": ['data', 'schemaName']
    }


@pytest.fixture
def person_field(dog_field):
    class PersonField(ObjectField):
        name = CharField(required=True)
        favourite_dog = dog_field()
    return PersonField


@pytest.fixture
def person_schema(dog_schema):
    dog_schema['title'] = 'Favourite Dog'
    return {
        'type': 'object',
        'title': 'Person',
        'properties': {
            'name': {
                'title': 'Name',
                'type': 'string',
                'format': 'text',
                'minLength': 1
            },
            'favourite_dog': dog_schema
        },
        'required': ['name']
    }


@pytest.fixture
def fish_field():
    class FishField(ObjectField):
        name = CharField(required=True)
        salt_water = BooleanField(default=False)
    return FishField


@pytest.fixture
def fish_schema():
    return {
        'type': 'object',
        'title': 'Fish',
        'properties': {
            'name': {
                'title': 'Name',
                'type': 'string',
                'format': 'text',
                'minLength': 1
            },
            'salt_water': {
                'title': 'Salt Water',
                'type': 'boolean',
                'format': 'checkbox',
                'default': False
            }
        },
        'required': ['name']
    }


@pytest.fixture
def typed_fish_schema(fish_schema):
    schema_name = 'fish'
    return {
        'type': 'object',
        'title': 'Fish',
        'properties': {
            'schemaName': {
                'title': 'Schema Name',
                'const': schema_name,
                'type': 'string',
                'default': schema_name,
                'template': schema_name
            },
            'data': fish_schema
        },
        "defaultProperties": ["data", "schemaName"],
        "required": ['data', 'schemaName']
    }


@pytest.fixture
def generic_animal_field():

    class GenericAnimalField(ObjectField):
        name = CharField(required=True)

        class Meta:
            abstract = True

        @property
        def loud_name(self):
            return self.name.upper()

    return GenericAnimalField


@pytest.fixture
def parrot_field(generic_animal_field):
    """
    A parrot field subclasses generic animal field
    """

    class ParrotField(generic_animal_field):
        talks = BooleanField(required=True)

        class Meta:
            schema_name = "squawker"

    return ParrotField


@pytest.fixture
def parrot_schema():
    return {
        'type': 'object',
        'title': 'Squawker',
        'properties': {
            'name': {
                'title': 'Name',
                'type': 'string',
                'format': 'text',
                'minLength': 1
            },
            'talks': {
                'title': 'Talks',
                'type': 'boolean',
                'format': 'checkbox'
            }
        },
        'required': ['name', 'talks']
    }


@pytest.fixture
def typed_parrot_schema(parrot_schema):
    schema_name = 'squawker'
    return {
        'type': 'object',
        'title': 'Squawker',
        'properties': {
            'schemaName': {
                'title': 'Schema Name',
                'const': schema_name,
                'type': 'string',
                'default': schema_name,
                'template': schema_name
            },
            'data': parrot_schema
        },
        "defaultProperties": ["data", "schemaName"],
        "required": ['data', 'schemaName']
    }


@pytest.fixture
def record_shop_form_class():
    class RecordShopForm(ModelForm):
        class Meta:
            model = RecordShop
            fields = ['name', 'catalog']

    return RecordShopForm
