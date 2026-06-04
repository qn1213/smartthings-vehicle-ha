from custom_components.smartthings_vehicle.vehicle import discover_vehicle_devices


def test_discover_vehicle_devices_returns_only_smartthings_devices_with_vehicle_capabilities():
    payload = {
        "items": [
            {
                "deviceId": "vehicle-1",
                "label": "쏘나타",
                "name": "hyundai-sonata",
                "manufacturerName": "Hyundai",
                "components": [
                    {
                        "id": "main",
                        "capabilities": [
                            {"id": "vehicleRange"},
                            {"id": "vehicleDoorState"},
                        ],
                    }
                ],
            },
            {
                "deviceId": "bulb-1",
                "label": "거실등",
                "components": [
                    {"id": "main", "capabilities": [{"id": "switch"}]}
                ],
            },
        ]
    }

    vehicles = discover_vehicle_devices(payload)

    assert vehicles == [
        {
            "device_id": "vehicle-1",
            "label": "쏘나타",
            "manufacturer": "Hyundai",
        }
    ]


def test_discover_vehicle_devices_uses_name_when_label_is_missing():
    payload = {
        "items": [
            {
                "deviceId": "vehicle-2",
                "name": "kia-ev6",
                "components": [
                    {"id": "main", "capabilities": [{"id": "vehicleEngine"}]}
                ],
            }
        ]
    }

    assert discover_vehicle_devices(payload) == [
        {"device_id": "vehicle-2", "label": "kia-ev6", "manufacturer": None}
    ]
