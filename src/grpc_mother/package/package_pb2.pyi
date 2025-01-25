from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor


class packageRequest(_message.Message):
    __slots__ = ["client_key", "type_ai"]
    CLIENT_KEY_FIELD_NUMBER: _ClassVar[int]
    TYPE_AI_FIELD_NUMBER: _ClassVar[int]
    client_key: str
    type_ai: str

    def __init__(self, client_key: _Optional[str] = ..., type_ai: _Optional[str] = ...) -> None: ...


class PackageExistRequest(_message.Message):
    __slots__ = ["client_key", "id", "is_superuser", "is_staff", "type_ai"]
    CLIENT_KEY_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_SUPERUSER_FIELD_NUMBER: _ClassVar[int]
    IS_STAFF_FIELD_NUMBER: _ClassVar[int]
    TYPE_AI_FIELD_NUMBER: _ClassVar[int]
    client_key: str
    id: int
    is_superuser: str
    is_staff: str
    type_ai: str

    def __init__(self, client_key: _Optional[str] = ..., id: _Optional[int] = ..., is_superuser: _Optional[str] = ...,
                 is_staff: _Optional[str] = ..., type_ai: _Optional[str] = ...) -> None: ...


class PackageReply(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: _containers.RepeatedScalarFieldContainer[int]

    def __init__(self, id: _Optional[_Iterable[int]] = ...) -> None: ...


class PackageExistReply(_message.Message):
    __slots__ = ["is_exist"]
    IS_EXIST_FIELD_NUMBER: _ClassVar[int]
    is_exist: str

    def __init__(self, is_exist: _Optional[str] = ...) -> None: ...
