from .service import ScenarioCollectionCreator

scenario_factory = ScenarioCollectionCreator()
scenario_collection = scenario_factory.create_collection()


def initialize():
    scenarios = ['a', 'b', 'c']
    for scenario in scenarios:
        data = {"name": scenario}
        scenario_collection.insert(data)
