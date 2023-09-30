# Discovery Service

This service is responsible for acting as a registry of what services are alive, and their network locations. In the
future, its responsibilities may extend to the number of microservice instances to intelligently scale the application.

# Stack
- RabbitMQ message bus (abstracted in [BusClient.py](../Common/BusClient.py))
- Redis for task queue (abstracted in [TaskQueue.py](../Common/TaskQueue.py)) for allowing multiple concurrent front-end
  instances to serve concurrent requests.