import inspect
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
    if re.match(r"^[a-zA-Z0-9\-_/:]*$", s):
        return s
    raise ValueError(
        f"Invalid name: '{s}'. Name must only contain alphanumeric "
        + "characters, dashes, underscores, and colons."
    )


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
