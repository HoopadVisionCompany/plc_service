import sys

sys.path.append('../..')
from src.controller_backend.service import ControllerCollectionCreator
from src.pin.service import PinCollectionCreator
from src.scenario.service import ScenarioCollectionCreator
from src.task.service import TaskCollectionCreator

controller_factory = ControllerCollectionCreator()
controller_collection = controller_factory.create_collection()

controller_factory = ControllerCollectionCreator()
controller_collection = controller_factory.create_collection()

pin_factory = PinCollectionCreator()
pin_collection = pin_factory.create_collection()

scenario_factory = ScenarioCollectionCreator()
scenario_collection = scenario_factory.create_collection()
task_factory = TaskCollectionCreator()
task_collection = task_factory.create_collection()


def create_controllers_info_dict():
    controller_info = {}
    controllers = controller_collection.retrieve()
    for controller in controllers:
        pin_numbers = []
        pins = list(pin_collection.pin_collection.find({"controller_id": controller["_id"]}))
        for pin in pins:
            pin_numbers.append(pin["number"])
        if 'driver' not in controller.keys():
            controller['driver'] = None
        controller_info[controller['name']] = {
            "Controller ID": controller["_id"],
            "Controller Type": controller['type'],
            "Controller Protocol": controller['protocol'],
            "Controller IP": controller['ip'],
            "Controller Port": controller['port'],
            "Controller Driver": controller['driver'],
            "Controller Unit": controller['controller_unit'],
            "Controller Count Pin IN": controller['count_pin_in'],
            "Controller Count Pin OUT": controller['count_pin_out'],
            "Controller Pins": pin_numbers,
        }

    return controller_info


# print(create_controllers_info_dict())


def create_controller_event_dict(task_id):
    controller_event = {}
    task = task_collection.detail(task_id)[0]
    # print("task", task)

    controller = controller_collection.detail(task["controller_id"])
    # print("controller", controller)

    pins = list(pin_collection.pin_collection.find(
        {"controller_id": task["controller_id"], "number": {"$in": task["pin_numbers"]}},
        {'number': 1, "type": 1, "delay": 1, "_id": 1}))
    # print("pins", pins)

    scenario = scenario_collection.detail(task["scenario_id"])
    # print("scenario", scenario)
    if 'driver' not in controller.keys():
        controller['driver'] = None
    # controller_event[controller['name']] = {
    #     "Controller ID": controller["_id"],
    #     "Controller Type": controller['type'],
    #     "Controller Protocol": controller['protocol'],
    #     "Controller IP": controller['ip'],
    #     "Controller Port": controller['port'],
    #     "Controller Driver": controller['driver'],
    #     "Controller Unit": controller['controller_unit'],
    #     "Controller Count Pin IN": controller['count_pin_in'],
    #     "Controller Count Pin OUT": controller['count_pin_out']
    # }
    # controller_event[controller['name']] = [controller["_id"], controller['type'], controller['protocol'],
    #                                         controller['ip'], controller['port'], controller['driver'],
    #                                         controller['controller_unit'], controller['count_pin_in'],
    #                                         controller['count_pin_out']]
    # controller_event_1 = {'Controller ID': 30,
    #                       'Pin List': [0, 1, 2],
    #                       'Pin Type': [],
    #                       'Scenario': 'Relay OFF'
    #                       }

    pin_list = []
    pin_id = []
    pin_type = []
    delay_list = []
    for pin in pins:
        print(pins)
        pin_list.append(pin["number"])
        pin_id.append(pin["_id"])
        pin_type.append(pin["type"])
        delay_list.append(pin["delay"])
    controller_event['Controller ID'] = controller['_id']
    controller_event['Pin List'] = pin_list
    controller_event['Pin ID'] = pin_id
    controller_event['Pin Type'] = pin_type
    controller_event['Delay List'] = delay_list
    controller_event['Scenario'] = scenario["name"]
    return controller_event


# a = create_controller_event_dict("ddb14f3a-7aba-478b-be99-23b7b96cd729")
# print(a)


def update_controllers_info_dict(data: dict):
    pins = list(pin_collection.pin_collection.find({"controller_id": data["_id"]}))
    pin_numbers = []
    controller_info = {}
    if 'driver' not in data.keys():
        data['driver'] = None
    if 'ip' not in data.keys():
        data['ip'] = None
    if 'port' not in data.keys():
        data['port'] = None
    for pin in pins:
        pin_numbers.append(pin["number"])
    controller_info["name"] = data["name"]
    controller_info["Controller ID"] = data["_id"]
    controller_info["Controller Type"] = data['type']
    controller_info["Controller Protocol"] = data['protocol']
    controller_info["Controller IP"] = data['ip']
    controller_info["Controller Port"] = data['port']
    controller_info["Controller Driver"] = data['driver']
    controller_info["Controller Unit"] = data['controller_unit']
    controller_info["Controller Count Pin IN"] = data['count_pin_in']
    controller_info["Controller Count Pin OUT"] = data['count_pin_out']
    controller_info["Controller Pins"] = pin_numbers

    return controller_info
