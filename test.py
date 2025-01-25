# [{
#   "_id": "cddefdda-7579-43e4-8624-413624589076",
#   "name": "Delta PLC",
#   "type": "PLC Delta",
#   "protocol": "Ethernet",
#   "ip": "192.168.10.5",
#   "port": 502,
#   "driver": "string",
#   "controller_unit": 1,
#   "count_pin_out": 8,
#   "count_pin_in": 4,
#   "count_total_pin": 12
# } ,
# {
#   "_id": "821d8f6f-a73b-4f3f-ad88-07e6a914c51c",
#   "name": "bluepill",
#   "type": "ARM Micro-controller",
#   "protocol": "Serial",
#   "ip": "0.0.0.0",
#   "port": 4000,
#   "driver": "/dev/ttyUSB0",
#   "controller_unit": 2,
#   "count_pin_out": 10,
#   "count_pin_in": 10,
#   "count_total_pin": 20
# }]

# [{
#   "_id": "45cf00c0-b5cf-425a-8805-60e15e9d0807",
#   "type": "in",
#   "controller_id": "cddefdda-7579-43e4-8624-413624589076",
#   "number": 1
# },
# {
#   "_id": "e577b41e-ebdf-486a-9099-5e4b8b888dcb",
#   "type": "in",
#   "controller_id": "cddefdda-7579-43e4-8624-413624589076",
#   "number": 2
# },
# {
#   "_id": "8a4c3630-4703-4c1d-a38b-88693f3b5310",
#   "type": "out",
#   "controller_id": "cddefdda-7579-43e4-8624-413624589076",
#   "number": 3
# },
# {
#   "_id": "1bde451e-9b0e-4167-9595-6401f296f8f2",
#   "type": "out",
#   "controller_id": "cddefdda-7579-43e4-8624-413624589076",
#   "number": 4
# },
# {
#   "_id": "f2a60c49-de6d-4198-a5c4-e1d13ae65097",
#   "type": "in",
#   "controller_id": "821d8f6f-a73b-4f3f-ad88-07e6a914c51c",
#   "number": 1
# },
# {
#   "_id": "aa24df5f-5f27-408c-86f4-b7dc6da80735",
#   "type": "out",
#   "controller_id": "821d8f6f-a73b-4f3f-ad88-07e6a914c51c",
#   "number": 2
# }]

# [{
#   "_id": "449e3873-d4ed-487a-82d5-abc778392d6e",
#   "name": "Relay ON"
# },
# {
#   "_id": "bbd087d3-2766-4aca-ab8d-b47284f2708c",
#   "name": "Relay OFF"
# },
# {
#   "_id": "5606fb01-fb9f-4dac-9d42-25ed9609666f",
#   "name": "c"
# }]

# [{
#   "_id": "d7be635c-994f-4db0-89f1-908906b8515a",
#   "name": "aa",
#   "description": "aaaaaaaa",
#   "controller_id": "cddefdda-7579-43e4-8624-413624589076",
#   "pin_numbers": [
#     1,
#     2,
#     3,
#     4
#   ],
#   "scenario_id": "449e3873-d4ed-487a-82d5-abc778392d6e"
# },
# {
#   "_id": "e6c5704c-122d-417e-b5f4-aca7a2851b7e",
#   "name": "bbbbbb",
#   "description": "bbbbbbbbbbbb",
#   "controller_id": "821d8f6f-a73b-4f3f-ad88-07e6a914c51c",
#   "pin_numbers": [
#     1,
#     2
#   ],
#   "scenario_id": "bbd087d3-2766-4aca-ab8d-b47284f2708c"
# }]

from src.pin.service import PinCollectionCreator
collection=PinCollectionCreator()
a=collection.create_collection()
b=a.get_collection()
b.find({})
b.update_one({"_id":"aa24df5f-5f27-408c-86f4-b7dc6da80735"},{"$set":{"delay":0}})
