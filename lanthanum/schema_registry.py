schema_registry = {}


def get_python_type(schema_name):
    """
    Get the python type for a given schema name
    """
    field = schema_registry[schema_name]
    return field.Meta.python_type
