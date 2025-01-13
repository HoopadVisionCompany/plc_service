from fastapi import Header
from src.grpc_mother.user.user import get_user
from src.utils.exceptions.custom_exceptions import CustomException401


def retrieve_user(
        token: str = Header(
            default="Bearer ",
            convert_underscores=False,
            description="JWT in the header"
        )
):
    auth_key = token[7:]
    user = get_user(auth_key)
    if not user:
        raise CustomException401("Can't access to this section")
    user["key_auth"] = auth_key

    return user
