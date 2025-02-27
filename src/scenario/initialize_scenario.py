import sys
sys.path.append('../')
from src.scenario.service import ScenarioCollectionCreator

scenario_factory = ScenarioCollectionCreator()
scenario_collection = scenario_factory.create_collection()


def initialize():
    scenarios = ['Auto Relay']
    for scenario in scenarios:
        data = {"name": scenario}
        scenario_collection.insert(data)
