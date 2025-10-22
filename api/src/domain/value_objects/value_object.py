from typing import Any, ClassVar
from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel):
    """
    Base class for immutable value objects in domain.
    Subclasses must define at least one field.
    Fields with `repr=False` are omitted from repr.
    If all fields are hidden, repr shows '<hidden>'.
    """

    model_config = ConfigDict(frozen=True)

    _is_base_class: ClassVar[bool] = True

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._is_base_class = False

    def __new__(cls, *args: Any, **kwargs: Any) -> "ValueObject":
        if cls._is_base_class:
            raise TypeError("Base ValueObject cannot be instantiated directly.")
        return super().__new__(cls)

    def __init__(self, **kwargs: Any) -> None:
        if not type(self).model_fields:
            raise TypeError(f"{type(self).__name__} must have at least one field!")
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__repr_value()})"

    def __repr_value(self) -> str:
        visible_fields = [
            (name, field)
            for name, field in type(self).model_fields.items()
            if getattr(field, "repr", True)
        ]

        if not visible_fields:
            return "<hidden>"

        values = []
        for name, _ in visible_fields:
            values.append(getattr(self, name))

        if len(visible_fields) == 1:
            return repr(values[0])
        else:
            pairs = [f"{name}={getattr(self, name)!r}" for name, _ in visible_fields]
            return ", ".join(pairs)
