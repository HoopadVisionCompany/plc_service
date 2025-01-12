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


print(create_controllers_info_dict())

# def create_controller_event_dict():
#     controller_event={}
#     controller_event = {
#         'Controller Name': [Controller ID, Controller Type, Controller Protocol, Controller IP, Controller Port,
#                             Controller Driver, Controller Unit, Controller Count Pin IN, Controller Count Pin OUT],
#         'Pin List': [],
#         'Pin Type': [],
#         'Scenario': ''
#         }
