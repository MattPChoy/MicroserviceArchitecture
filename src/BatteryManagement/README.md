# Battery Management Microservice

The battery management microservice sourcecode (mainly) lives here, except for the API
specification which is contained in [Gateway/Views/BatteryManagement.py](../Gateway/Views/BatteryManagement.py).

## Notes

- The Dockerfile is constructed in such a way that it must be run in the build context of the parent (root)
  directory, `src/`.

## Stack and Dependencies
- RabbitMQ message bus (abstracted in [BusClient.py](../Common/BusClient.py))
- PostgreSQL database for battery persistence (abstracted in the BatteryTable class
  in [Battery.py](..Gateway/models/Battery.py)