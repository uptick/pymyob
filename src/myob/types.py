from typing import Literal, TypedDict

# TODO: This could probs do better as an enum..
Method = Literal["ALL", "GET", "POST", "PUT", "DELETE"]


class MethodDetails(TypedDict):
    kwargs: list[str]
    hint: str
