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
            "Controller Count Pin OUT": controller['count_pin_out']
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
        {'number': 1, "type": 1, "_id": 0}))
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
    pin_type = []
    for pin in pins:
        pin_list.append(pin["number"])
        pin_type.append(pin["type"])
    controller_event['Controller ID'] = controller['_id']
    controller_event['Pin List'] = pin_list
    controller_event['Pin Type'] = pin_type
    controller_event['Scenario'] = scenario["name"]
    return controller_event

# a = create_controller_event_dict("ddb14f3a-7aba-478b-be99-23b7b96cd729")
# print(a)
