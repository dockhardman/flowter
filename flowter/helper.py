import inspect
import keyword
import random
import re
import string
import typing
from types import MappingProxyType


def str_or_none(s: typing.Text) -> typing.Optional[typing.Text]:
    if isinstance(s, typing.Text):
        s = s.strip()
        if s:
            return s
    return None


def rand_str(length: int = 10) -> typing.Text:
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


def validate_name(s: typing.Text) -> typing.Text:
    if re.match(r"^[a-zA-Z0-9\-_/:]+$", s):
        return s
    raise ValueError(
        f"Invalid name: '{s}'. Name must only contain alphanumeric "
        + "characters, dashes, underscores, and colons."
    )


def validate_params_name(
    name: typing.Text,
    replace_hyphen: typing.Optional[typing.Text] = None,
    replace_slash: typing.Optional[typing.Text] = None,
    replace_colon: typing.Optional[typing.Text] = None,
    strip_whitespace: bool = False,
    strip_text: typing.Optional[typing.Text] = None,
) -> typing.Text:
    if not isinstance(name, typing.Text):
        raise ValueError(f"Invalid parameter type: '{name}'")
    # Remove leading and trailing whitespaces
    if strip_whitespace:
        name = name.strip()
    # Remove leading and trailing text
    if isinstance(strip_text, typing.Text):
        name = name.strip(strip_text)
    # Replace colons with underscores
    if isinstance(replace_colon, typing.Text):
        name = name.replace(":", replace_colon)
    # Replace slashes with underscores
    if isinstance(replace_slash, typing.Text):
        name = name.replace("/", replace_slash)
    # Replace hyphens with underscores
    if isinstance(replace_hyphen, typing.Text):
        name = name.replace("-", replace_hyphen)
    # Check if it's a valid Python identifier
    if not name.isidentifier():
        raise ValueError(f"Invalid parameter name: '{name}'")
    # Check if it's a Python keyword
    if keyword.iskeyword(name):
        raise ValueError(f"Invalid parameter name: '{name}'")
    return name


def collect_params(
    signature_parameters: MappingProxyType[typing.Text, "inspect.Parameter"],
    *args,
    kwargs: typing.Optional[typing.Dict[typing.Text, typing.Any]] = None,
    **extra_kwargs,
) -> typing.Tuple[typing.Tuple[typing.Any, ...], typing.Dict[typing.Text, typing.Any]]:
    collected_args = []
    collected_kwargs = {}
    args_idx = 0
    args_name_pool = set()
    for param_name, param_meta in signature_parameters.items():
        if param_meta.kind == inspect.Parameter.POSITIONAL_ONLY:
            collected_args.append(args[args_idx])
            args_idx += 1
            args_name_pool.add(param_name)
        elif param_meta.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD:
            # Keyword arguments have priority over positional arguments
            if kwargs and param_name in kwargs and param_name not in args_name_pool:
                collected_kwargs[param_name] = kwargs[param_name]
            elif param_name in extra_kwargs and param_name not in args_name_pool:
                collected_kwargs[param_name] = extra_kwargs[param_name]
            elif args_idx < len(args):
                collected_args.append(args[args_idx])
                args_idx += 1
                args_name_pool.add(param_name)
            elif param_meta.default != inspect.Parameter.empty:
                collected_kwargs[param_name] = param_meta.default
            else:
                raise TypeError(f"Missing required positional argument: '{param_name}'")
        elif param_meta.kind == inspect.Parameter.VAR_POSITIONAL:
            collected_args.extend(args[args_idx:])
            args_idx = len(args)
        elif param_meta.kind == inspect.Parameter.KEYWORD_ONLY:
            if kwargs and param_name in kwargs and param_name not in args_name_pool:
                collected_kwargs[param_name] = kwargs[param_name]
            elif param_meta.default != inspect.Parameter.empty:
                collected_kwargs[param_name] = param_meta.default
            elif param_name in extra_kwargs and param_name not in args_name_pool:
                collected_kwargs[param_name] = extra_kwargs[param_name]
            else:
                raise TypeError(f"Missing required keyword argument: '{param_name}'")
        elif param_meta.kind == inspect.Parameter.VAR_KEYWORD:
            if kwargs:
                for k, v in kwargs.items():
                    if k not in collected_kwargs and k not in args_name_pool:
                        collected_kwargs[k] = v
            if extra_kwargs:
                for k, v in extra_kwargs.items():
                    if k not in collected_kwargs and k not in args_name_pool:
                        collected_kwargs[k] = v
        else:
            raise TypeError(f"Unsupported parameter type: '{param_meta.kind}'")

    return (tuple(collected_args), collected_kwargs)
