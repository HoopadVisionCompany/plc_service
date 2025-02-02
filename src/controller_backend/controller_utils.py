from src.controller.controller import Controller
from src.utils.controller_dict_creator import update_controllers_info_dict


def update_controller_info_insert(data: dict):
    print("before : ", Controller({}).controller_info)
    controller_info = update_controllers_info_dict(data)
    Controller({}).update_controller_info(controller_info)
    print("after : ", Controller({}).controller_info)


def update_controller_info_update(data_before_update: dict, data_after_update: dict):
    print("before : ", Controller({}).controller_info)
    controller_info = update_controllers_info_dict(data_after_update)
    del Controller({}).controller_info[data_before_update["name"]]
    Controller({}).update_controller_info(controller_info)
    print("after : ", Controller({}).controller_info)


def update_controller_info_delete(data: dict):
    print("before : ", Controller({}).controller_info)
    del Controller({}).controller_info[data["name"]]
    print("after : ", Controller({}).controller_info)
