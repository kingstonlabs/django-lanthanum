from lanthanum.schema_fields import ObjectField, CharField, DynamicArrayField


class SingleField(ObjectField):
    class Meta:
        schema_name = "single"

    title = CharField(required=True)
    artist = CharField()


class AlbumField(ObjectField):
    title = CharField(required=True)


music_catalog_field = DynamicArrayField(
    allowed_fields=[
        SingleField(),
        AlbumField()
    ],
    item_label="Product"
)
