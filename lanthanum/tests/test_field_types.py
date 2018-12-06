import pytest

from ..field_types import DynamicObject, TypedArray, DynamicArray


@pytest.fixture
def dog_type():
    class DogType(DynamicObject):
        name = str
        breed = str
    return DogType


@pytest.fixture
def fish_type():
    class FishType(DynamicObject):
        name = str
        salt_water = bool
    return FishType


@pytest.fixture
def person_type(dog_type):
    class PersonType(DynamicObject):
        name = str
        favourite_dog = dog_type
    return PersonType


@pytest.fixture
def dog_array_type(dog_type):
    class DogArrayType(TypedArray):
        class Meta:
            schema_type = 'array'
            base_type = dog_type
    return DogArrayType


class TestDynamicObject:
    def test_simple_type(self, dog_type, scooby_doo):
        dog_instance = dog_type(scooby_doo)
        assert dog_instance.name == scooby_doo['name']
        assert dog_instance.breed == scooby_doo['breed']

    def test_nested_type(self, person_type, shaggy, scooby_doo):
        person_instance = person_type(shaggy)
        assert person_instance.name == shaggy['name']
        assert person_instance.favourite_dog.name == scooby_doo['name']
        assert person_instance.favourite_dog.breed == scooby_doo['breed']


class TestTypedArray:
    def test_simple_array(self, dog_array_type, scooby_doo, snoopy):
        dog_array = dog_array_type([scooby_doo, snoopy])

        assert len(dog_array) == 2
        scooby_doo_instance = dog_array[0]
        snoopy_instance = dog_array[1]
        assert scooby_doo_instance.name == scooby_doo['name']
        assert scooby_doo_instance.breed == scooby_doo['breed']
        assert snoopy_instance.name == snoopy['name']
        assert snoopy_instance.breed == snoopy['breed']
        assert str(dog_array) == str([scooby_doo_instance, snoopy_instance])
        assert repr(dog_array) == str([scooby_doo_instance, snoopy_instance])

    def test_simple_array_update(self, dog_array_type, scooby_doo, snoopy):
        dog_array = dog_array_type([scooby_doo, snoopy])

        assert len(dog_array) == 2
        dog_array[1] = scooby_doo
        assert len(dog_array) == 2

        item_2 = dog_array[1]
        assert item_2.name == scooby_doo['name']
        assert item_2.breed == scooby_doo['breed']

    def test_simple_array_del(self, dog_array_type, scooby_doo, snoopy):
        dog_array = dog_array_type([scooby_doo, snoopy])

        assert len(dog_array) == 2
        del dog_array[1]
        assert len(dog_array) == 1


class TestDynamicArray:
    @pytest.fixture(autouse=True)
    def schema_registry(self, monkeypatch, dog_type, fish_type):
        class MockDogSchema(object):
            class Meta:
                python_type = dog_type

        class MockFishSchema(object):
            class Meta:
                python_type = fish_type

        monkeypatch.setattr(
            'lanthanum.schema_registry.schema_registry',
            {'dog': MockDogSchema, 'fish': MockFishSchema}
        )

    def test_simple_array(self, scooby_doo, nemo):
        pet_array = DynamicArray(
            [
                {'schemaName': 'dog', 'data': scooby_doo},
                {'schemaName': 'fish', 'data': nemo}
            ]
        )

        assert len(pet_array) == 2
        scooby_doo_instance = pet_array[0]
        nemo_instance = pet_array[1]
        assert scooby_doo_instance.name == scooby_doo['name']
        assert scooby_doo_instance.breed == scooby_doo['breed']
        assert nemo_instance.name == nemo['name']
        assert nemo_instance.salt_water == nemo['salt_water']
        assert str(pet_array) == str([scooby_doo_instance, nemo_instance])
        assert repr(pet_array) == str([scooby_doo_instance, nemo_instance])

    def test_simple_array_update(self, scooby_doo, snoopy, nemo):
        pet_array = DynamicArray(
            [
                {'schemaName': 'dog', 'data': scooby_doo},
                {'schemaName': 'fish', 'data': nemo}
            ]
        )

        assert len(pet_array) == 2
        pet_array[1] = {'schemaName': 'dog', 'data': snoopy}
        item_2 = pet_array[1]
        assert item_2.name == snoopy['name']
        assert item_2.breed == snoopy['breed']

    def test_simple_array_del(self, scooby_doo, nemo):
        pet_array = DynamicArray(
            [
                {'schemaName': 'dog', 'data': scooby_doo},
                {'schemaName': 'fish', 'data': nemo}
            ]
        )

        assert len(pet_array) == 2
        del pet_array[1]
        assert len(pet_array) == 1
