from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, \
    Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor


class userRequest(_message.Message):
    __slots__ = ["client_key"]
    CLIENT_KEY_FIELD_NUMBER: _ClassVar[int]
    client_key: str

    def __init__(self, client_key: _Optional[str] = ...) -> None: ...


class usersRequest(_message.Message):
    __slots__ = ["version_id"]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    version_id: int

    def __init__(self, version_id: _Optional[int] = ...) -> None: ...


class userReply(_message.Message):
    __slots__ = ["id", "user_name", "is_superuser", "is_staff", "version_id", "type_id", "title"]
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    IS_SUPERUSER_FIELD_NUMBER: _ClassVar[int]
    IS_STAFF_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_name: str
    is_superuser: str
    is_staff: str
    version_id: int
    type_id: int
    title: str

    def __init__(self, id: _Optional[int] = ..., user_name: _Optional[str] = ..., is_superuser: _Optional[str] = ...,
                 is_staff: _Optional[str] = ..., version_id: _Optional[int] = ..., type_id: _Optional[int] = ...,
                 title: _Optional[str] = ...) -> None: ...


class userReply2(_message.Message):
    __slots__ = ["id", "user_name", "version_id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_name: str
    version_id: int

    def __init__(self, id: _Optional[int] = ..., user_name: _Optional[str] = ...,
                 version_id: _Optional[int] = ...) -> None: ...


class userListReply(_message.Message):
    __slots__ = ["results"]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.RepeatedCompositeFieldContainer[userReply2]

    def __init__(self, results: _Optional[_Iterable[_Union[userReply2, _Mapping]]] = ...) -> None: ...
