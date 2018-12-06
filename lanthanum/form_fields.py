def to_schema_field(field_class):
    """
    Wraps a field class to ensure that it extracts the data from JSON Schema.
    """
    class DynamicJSONField(field_class):
        def prepare_value(self, value):
            """
            Use the raw field data in the JSON field.
            """
            if value is None:
                return value
            return super().prepare_value(getattr(value, '_data', value))

    return DynamicJSONField
