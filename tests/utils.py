import typing


def func_add(a: int, b: int) -> int:
    return a + b


def func_concat(i: typing.Text, j: typing.Text, *args) -> typing.Text:
    return str(i) + str(j) + "".join(str(k) for k in args)


def func_merge(data: typing.Dict, **kwargs) -> typing.Dict:
    data.update(kwargs)
    return data


def func_key_value_table(title: typing.Text, /, **kwargs) -> typing.Text:
    content = f"{title}\n"
    for k, v in kwargs.items():
        content += f"{k}: {v}\n"
    return content
