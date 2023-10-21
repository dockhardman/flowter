import typing

import pytest

from flowter.helper import collect_params, rand_str, str_or_none, validate_name


@pytest.mark.parametrize(
    "s, expected",
    [
        ("", None),
        (" ", None),
        ("a", "a"),
        (" a ", "a"),
        ("a b", "a b"),
        ("a\nb ", "a\nb"),
        (1, None),
    ],
)
def test_str_or_none(s: typing.Text, expected: typing.Optional[typing.Text]):
    assert str_or_none(s) == expected


def test_rand_str():
    assert len(rand_str()) == 10  # default length
    assert len(rand_str(5)) == 5


@pytest.mark.parametrize(
    "s, passed",
    [
        ("", False),
        (" ", False),
        ("a", True),
        ("a b", False),
        ("a\nb", False),
        ("a-b", True),
        ("a_b", True),
        ("a:b", True),
        ("a/b", True),
        ("a:b/c", True),
    ],
)
def test_validate_name(s: typing.Text, passed: bool):
    if passed:
        assert validate_name(s) == s
    else:
        try:
            validate_name(s)
            assert False, f"validate_name('{s}') should raise ValueError"
        except ValueError:
            pass
