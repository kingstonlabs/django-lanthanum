import re


def camel_to_underscore(string_in):
    """
    Convert a camel case string to an underscored string
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string_in)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def strip_suffix(string_in, suffix):
    """
    Strip a suffix from a string
    """
    if string_in.endswith(suffix):
        return string_in[:-len(suffix)]
    return string_in


def field_to_schema_name(field_name):
    """
    Convert a field class name to a schema name and remove the Field suffix
    """
    return camel_to_underscore(strip_suffix(field_name, "Field"))
