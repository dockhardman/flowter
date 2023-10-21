import inspect
import pprint
import typing

import pytest

from flowter.helper import (
    collect_params,
    rand_str,
    str_or_none,
    validate_name,
    validate_params_name,
)

from .utils import func_add, func_concat, func_key_value_table, func_merge


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


def test_collect_params():
    args = (1, 2, 3)
    kwargs = {"c": 7}
    extra_kwargs = dict(b=4, c=5, d=6)

    # Test args with kwargs
    collected_args, collected_kwargs = collect_params(
        inspect.signature(func_add).parameters, *args, kwargs=kwargs, **extra_kwargs
    )
    assert collected_args == (1, 4)
    assert pprint.pformat(collected_kwargs) == pprint.pformat({})

    # Test positional args
    collected_args, collected_kwargs = collect_params(
        inspect.signature(func_concat).parameters, *args, kwargs=kwargs, **extra_kwargs
    )
    assert collected_args == (1, 2, 3)
    assert pprint.pformat(collected_kwargs) == pprint.pformat({})

    # Test var kwargs
    collected_args, collected_kwargs = collect_params(
        inspect.signature(func_merge).parameters,
        *({"hello": "world"},),
        kwargs=kwargs,
        **extra_kwargs,
    )
    assert collected_args == ({"hello": "world"},)
    assert pprint.pformat(collected_kwargs) == pprint.pformat({"c": 7, "b": 4, "d": 6})

    # Test kwargs
    collected_args, collected_kwargs = collect_params(
        inspect.signature(func_key_value_table).parameters,
        *args,
        kwargs=kwargs,
        **extra_kwargs,
    )
    assert collected_args == (1,)
    assert pprint.pformat(collected_kwargs) == pprint.pformat({"c": 7, "b": 4, "d": 6})
