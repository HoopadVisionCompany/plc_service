scenario = [{"_id": "0010e97c-cd87-4151-9167-02512014d11a", "name": "Auto Alarm ON"},
            {"_id": "8425547f-de49-407f-b3a7-607b72300075", "name": "Auto Caller"},
            {"_id": "87bd4b01-ed2a-4c37-91bf-25940812ce5c", "name": "Manual Alarm ON"},
            {"_id": "f26263ce-a86b-4a56-ac9f-fcb7e57a0dd8", "name": "Relay ON"},
            {"_id": "29fde11b-a99b-43de-b432-0c6fbb574b55", "name": "Manual Alarm OFF"},
            {"_id": "c0ade193-a744-486d-a2e4-48b673b8e120", "name": "Relay OFF"},
            {"_id": "d8fce085-97be-447e-a066-cec06f957d2b", "name": "Auto Gate"},
            {"_id": "85a597d4-992c-4a8c-a88d-7d36d165ff20", "name": "Manual Gate Open"},
            {"_id": "acdcb8d6-ae78-4159-be23-803fccd6ecb4", "name": "Manual Gate Close"},

            ]
# scenario_ids = [
#     "0010e97c-cd87-4151-9167-02512014d11a",
#     "8425547f-de49-407f-b3a7-607b72300075",
#     "87bd4b01-ed2a-4c37-91bf-25940812ce5c",
#     "f26263ce-a86b-4a56-ac9f-fcb7e57a0dd8",
#     "29fde11b-a99b-43de-b432-0c6fbb574b55",
#     "c0ade193-a744-486d-a2e4-48b673b8e120",
#     "d8fce085-97be-447e-a066-cec06f957d2b",
#     "85a597d4-992c-4a8c-a88d-7d36d165ff20",
#     "acdcb8d6-ae78-4159-be23-803fccd6ecb4"
# ]

controller = [
    {"_id": "ceaf1d86-b4e5-447a-afc4-37acf8cdccaa", "name": "W", "type": "Alpha", "protocol": "Ethernet",
     "ip": "134.98.48.116", "port": 8050, "driver": "backup", "controller_unit": 1, "count_total_pin": 42,
     "count_pin_in": 7, "count_pin_out": 35},
    {"_id": "9b1e3c7a-e01a-42ac-afe0-77ee6f0a0dab", "name": "R", "type": "Alpha", "protocol": "DeviceNet",
     "ip": "255.114.238.63", "port": 8173, "driver": "primary", "controller_unit": 2, "count_total_pin": 57,
     "count_pin_in": 7, "count_pin_out": 50},
    {"_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff", "name": "J", "type": "Zimmense", "protocol": "DeviceNet",
     "ip": "156.131.214.43", "port": 8256, "driver": "emergency", "controller_unit": 3, "count_total_pin": 22,
     "count_pin_in": 3, "count_pin_out": 19},
    {"_id": "cea57e0c-41d5-466e-b9c9-b83a1c360c81", "name": "Z", "type": "Beta", "protocol": "ControlNet",
     "ip": "60.17.12.162", "port": 8073, "driver": "tertiary", "controller_unit": 4, "count_total_pin": 47,
     "count_pin_in": 3, "count_pin_out": 44},
    {"_id": "0e13928a-cf74-4077-894c-0ef6cfb3d365", "name": "N", "type": "Delta", "protocol": "Profinet",
     "ip": "195.19.64.209", "port": 8439, "driver": "primary", "controller_unit": 5, "count_total_pin": 28,
     "count_pin_in": 5, "count_pin_out": 23}
]
# controller_ids = [
#     "ceaf1d86-b4e5-447a-afc4-37acf8cdccaa",
#     "9b1e3c7a-e01a-42ac-afe0-77ee6f0a0dab",
#     "6b662149-ff81-408f-9ccc-a716a5cca0ff",
#     "cea57e0c-41d5-466e-b9c9-b83a1c360c81",
#     "0e13928a-cf74-4077-894c-0ef6cfb3d365"
# ]
pins = [{"_id": "2d75edab-33da-47bc-a9b0-56cd982b2b8d", "type": "in",
         "controller_id": "9b1e3c7a-e01a-42ac-afe0-77ee6f0a0dab", "number": 0, "delay": 10, "timer": 0},
        {"_id": "3d7b7ddb-b668-46ad-9cfa-0fbf4f7eda40", "type": "out",
         "controller_id": "9b1e3c7a-e01a-42ac-afe0-77ee6f0a0dab", "number": 1, "delay": 4, "timer": 1},
        {"_id": "4d8b8fce-e848-40e2-8f1f-efe4ed63bb3f", "type": "out",
         "controller_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff", "number": 3, "delay": 0, "timer": 2},
        {"_id": "c3bcf5fe-34f3-4d4b-9c73-a34c82cf55cd", "type": "out",
         "controller_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff", "number": 4, "delay": 4, "timer": 3},
        {"_id": "d38cca8e-cedf-4b28-af4c-3c6f9b3c5dd1", "type": "in",
         "controller_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff", "number": 2, "delay": 9, "timer": 4}
        ]
# pin_ids = [
#     "2d75edab-33da-47bc-a9b0-56cd982b2b8d",
#     "3d7b7ddb-b668-46ad-9cfa-0fbf4f7eda40",
#     "4d8b8fce-e848-40e2-8f1f-efe4ed63bb3f",
#     "c3bcf5fe-34f3-4d4b-9c73-a34c82cf55cd",
#     "d38cca8e-cedf-4b28-af4c-3c6f9b3c5dd1"
# ]
# pins_of_each_controller = {
#     "9b1e3c7a-e01a-42ac-afe0-77ee6f0a0dab": [
#         {"number": 0, "controller_id": "9b1e3c7a-e01a-42ac-afe0-77ee6f0a0dab"},
#         {"number": 1, "controller_id": "9b1e3c7a-e01a-42ac-afe0-77ee6f0a0dab"}
#     ],
#     "6b662149-ff81-408f-9ccc-a716a5cca0ff": [
#         {"number": 3, "controller_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff"},
#         {"number": 4, "controller_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff"},
#         {"number": 2, "controller_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff"}
#     ]
# }

task = [{"_id": "845ca63a-e9a2-43be-a896-8a72f8b67661", "name": "H", "description": "dummy5",
         "controller_id": "9b1e3c7a-e01a-42ac-afe0-77ee6f0a0dab", "pin_numbers": [0, 1],
         "scenario_id": "29fde11b-a99b-43de-b432-0c6fbb574b55"},
        {"_id": "ecabfab9-9acd-4a90-95f0-5819afc444e1", "name": "G", "description": "dummy1",
         "controller_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff", "pin_numbers": [2],
         "scenario_id": "0010e97c-cd87-4151-9167-02512014d11a"},
        {"_id": "7fe3b7cc-174b-48ff-9868-cf09abb8dbd7", "name": "E", "description": "dummy1",
         "controller_id": "6b662149-ff81-408f-9ccc-a716a5cca0ff", "pin_numbers": [3, 4],
         "scenario_id": "f26263ce-a86b-4a56-ac9f-fcb7e57a0dd8"},
        ]
