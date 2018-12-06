import json

from django.core.serializers import serialize
import pytest

from .mock_app.models import RecordShop


@pytest.fixture
def record_catalog():
    return [
        {
            'schemaName': 'single',
            'data': {
                'title': 'Scooby Snacks',
                'artist': 'Scooby Doo'
            }
        },
        {
            'schemaName': 'album',
            'data': {
                'title': 'Who Let The Dogs Out?'
            }
        }
    ]


@pytest.fixture
def alternative_record_catalog():
    return [
        {
            'schemaName': 'single',
            'data': {
                'title': 'D-O-G-G',
                'artist': 'Snoopy'
            }
        },
        {
            'schemaName': 'single',
            'data': {
                'title': 'The Cat in the Hat',
                'artist': 'Top Cat'
            }
        }
    ]


@pytest.fixture
def hmv_instance(record_catalog):
    hmv = RecordShop(name="HMV", catalog=record_catalog)
    hmv.save()
    hmv.refresh_from_db()
    return hmv


@pytest.mark.django_db
class TestFields:
    def test_load_json_to_dynamic_field(self, hmv_instance, record_catalog):
        """
        It should be possible to load json data directly into a dynamic field
        """
        item_1 = hmv_instance.catalog[0]
        assert item_1.title == record_catalog[0]['data']['title']

    def test_empty_data_to_dynamic_field(self, hmv_instance):
        """
        Allow empty dynamic fields
        """
        record_shop = RecordShop(name="OurPrice", catalog=None)
        record_shop.save()
        record_shop.refresh_from_db()
        assert record_shop.catalog is None

    def test_serialize_dynamic_field(self, hmv_instance, record_catalog):
        """
        Serialize the dynamic field to json
        """
        json_record_shops = serialize(
            format='json', queryset=RecordShop.objects.all()
        )
        assert json.loads(json_record_shops)[0]['fields'] == {
            "name": "HMV",
            "catalog": record_catalog
        }

    def test_add_form_field(
        self, alternative_record_catalog, record_shop_form_class
    ):
        record_shop_form = record_shop_form_class(
            {'name': 'virgin', 'catalog': alternative_record_catalog}
        )

        assert record_shop_form.is_valid()

        record_shop_form.save()
        virgin_instance = RecordShop.objects.get(name="virgin")
        assert len(virgin_instance.catalog) == len(alternative_record_catalog)

        item_1 = virgin_instance.catalog[0]
        assert item_1.title == alternative_record_catalog[0]['data']['title']
        assert item_1.artist == alternative_record_catalog[0]['data']['artist']

        item_2 = virgin_instance.catalog[1]
        assert item_2.title == alternative_record_catalog[1]['data']['title']
        assert item_2.artist == alternative_record_catalog[1]['data']['artist']

    def test_update_form_field(
        self, hmv_instance, alternative_record_catalog, record_shop_form_class
    ):
        record_shop_form = record_shop_form_class(
            {
                'name': 'HMV',
                'catalog': alternative_record_catalog
            },
            instance=hmv_instance
        )

        assert record_shop_form.is_valid()

        record_shop_form.save()

        hmv_instance.refresh_from_db()
        assert len(hmv_instance.catalog) == len(alternative_record_catalog)

        item_1 = hmv_instance.catalog[0]
        assert item_1.title == alternative_record_catalog[0]['data']['title']
        assert item_1.artist == alternative_record_catalog[0]['data']['artist']

        item_2 = hmv_instance.catalog[1]
        assert item_2.title == alternative_record_catalog[1]['data']['title']
        assert item_2.artist == alternative_record_catalog[1]['data']['artist']

    def test_render_empty_form_field_widget(self, record_shop_form_class):
        record_shop_form = record_shop_form_class()

        widget = record_shop_form.fields['catalog'].widget
        assert widget.template_name == "lanthanum/_json_editor_widget.html"
        # Just check the widget is able to render something
        assert widget.render(name="catalog", value=None)
