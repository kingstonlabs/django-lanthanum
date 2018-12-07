import unittest


def assert_list_equal(expected, actual, ignore_order=True):
    """
    Assert two lists are equal, but also provides the option to ignore order
    """
    assert isinstance(actual, list)

    if ignore_order:
        test_case = unittest.TestCase()
        test_case.assertCountEqual(expected, actual)
    else:
        assert expected == actual


def assert_dict_equal(expected, actual, ignore_list_order=True):
    """
    Iterate over dict and assert each part is equal

    This will cause an assertion error on the first difference, but should be
    more informative than a standard assertion as it will specify exactly
    where the difference is.
    """
    assert isinstance(actual, dict)
    assert expected.keys() == actual.keys()
    for key, value in expected.items():
        if isinstance(value, dict):
            assert_dict_equal(value, actual[key])
        elif isinstance(value, list):
            assert_list_equal(
                value,
                actual[key],
                ignore_order=ignore_list_order
            )
        else:
            assert value == actual[key]
