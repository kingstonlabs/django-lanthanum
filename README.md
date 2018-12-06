Django Lanthanum
================

Django Lanthanum allows you to add Dynamic [JSON Schema](https://json-schema.org/) Fields to your models. These allow you to build complex documents according to a set of fixed criteria - since the schema is fixed, it is possible to properly interpret the data.

This could be applied to a wide variety of scenarios, but it is particularly useful for Blogging or CMS tools, where the data structure of a page document can vary significantly.


Testing
-------

To test the package, run `tox` - this will run against each of the supported environments. To run for a specific environment, provide the appropriate flag, for example: `tox -e py36-django21`
