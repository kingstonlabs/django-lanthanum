import copy

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.forms import JSONField as JSONFormField

from .form_fields import to_schema_field
from .widgets import JSONEditorWidget


class DynamicField(JSONField):
    description = "A dynamic field for json schema data"

    def __init__(self, *args, **kwargs):
        self.schema_field = kwargs.pop("schema_field")
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.schema_field is not None:
            kwargs['schema_field'] = self.schema_field
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        """
        Convert the data coming out of the database into a schema field object.
        """
        if value is None:
            return value

        schema_field = copy.deepcopy(self.schema_field)
        schema_field.load_data(value)

        return schema_field

    def value_to_string(self, obj):
        """
        Convert object to data for data dumps.
        """
        value = self.value_from_object(obj)
        return value.data

    def formfield(self, **kwargs):
        """
        Provide a JSON Editor Widget to work with the data.
        """
        widget = JSONEditorWidget(
            self.schema_field.schema,
            collapsed=False
        )
        defaults = {'form_class': JSONFormField, 'widget': widget}
        defaults.update(kwargs)
        defaults['form_class'] = to_schema_field(defaults['form_class'])
        return super().formfield(**defaults)