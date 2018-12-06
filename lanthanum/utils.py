import re


def camel_to_underscore(string_in):
    """
    Convert a camel case string to an underscored string
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string_in)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def field_to_schema_name(field_name):
    """
    Convert a field class name to a schema name

    This strips off the Field suffix and converts camelcase to underscores.
    """
    if field_name.endswith("Field"):
        field_suffix_length = 5                 # = len("Field")
        field_name = field_name[:-field_suffix_length]
    return camel_to_underscore(field_name)
