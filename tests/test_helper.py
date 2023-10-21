import typing

import pytest

from flowter.helper import (
    collect_params,
    rand_str,
    str_or_none,
    validate_name,
    validate_params_name,
)


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


@pytest.mark.parametrize(
    "name, replace_hyphen, replace_slash, replace_colon, strip_whitespace, strip_text, expected",
    [
        ("parameter", None, None, None, False, None, "parameter"),
        (" parameter ", None, None, None, True, None, "parameter"),
        ("parameter:", "-", None, "_", False, None, "parameter_"),
        ("parameter/", None, "_", None, False, None, "parameter_"),
        ("parameter-", "_", None, None, False, None, "parameter_"),
        (" prefix:parameter/ ", "_", "_", "_", True, "prefix", "_parameter_"),
        ("123parameter", None, None, None, False, None, ValueError),
        ("lambda", None, None, None, False, None, ValueError),
    ],
)
def test_validate_params_name(
    name,
    replace_hyphen,
    replace_slash,
    replace_colon,
    strip_whitespace,
    strip_text,
    expected,
):
    if expected is ValueError:
        with pytest.raises(ValueError):
            validate_params_name(
                name,
                replace_hyphen=replace_hyphen,
                replace_slash=replace_slash,
                replace_colon=replace_colon,
                strip_whitespace=strip_whitespace,
                strip_text=strip_text,
            )
    else:
        result = validate_params_name(
            name,
            replace_hyphen=replace_hyphen,
            replace_slash=replace_slash,
            replace_colon=replace_colon,
            strip_whitespace=strip_whitespace,
            strip_text=strip_text,
        )
        assert result == expected
