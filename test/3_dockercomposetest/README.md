# RabbitMQ Docker Container Orchestration

## Startup

To run this project, you can use the `docker compose` command. The following command spawns 2 instances of the producer
microservice and 4 instances of the consumer microservice.

```bash
docker-compose up --scale producer=2 --scale consumer=4
```

## Mechanics
The docker-compose file is responsible for giving the instructions of spawning each container.
- The Dockerfile within `consumer/` and `producer/` provide instructions as to how each image should be built.
