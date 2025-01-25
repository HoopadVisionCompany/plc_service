from src.grpc_mother.package.package import get_packages
from src.grpc_mother.part.part import get_parts, get_parts_id
from src.utils.exceptions.custom_exceptions import CustomException400


def package_checker(key_auth: str, data: dict, user: dict):
    if data["package_id"] not in get_packages(key_auth):
        raise CustomException400(f"package {data['package_id']} is not available for {user['username']}")


def part_checker(key_auth: str, data: dict, user: dict):
    if data["part_id"] not in get_parts_id(get_parts(key_auth)):
        raise CustomException400(f"part {data['part_id']} is not available for {user['username']}")


def list_part_checker(key_auth: str, data: dict, user: dict):
    allowed_parts = get_parts_id(get_parts(key_auth))
    common_parts = list(set(allowed_parts) & set(data["part_id"]))
    if len(common_parts) == 0:
        raise CustomException400("please enter allowed partitions")
