# Microservice vs Monolithic Architecture Comparison

This test aims to validate the hypothesis that whilst a microservice architecture with low replica counts will probably
be outperformed by a Monolithic architecture, with higher replica counts will significantly outperform a Monolithic
architecture.

This test simulates a load of inserting a battery record into a Postgresql database.

## Run Tests

To run the tests, there are a few commands to be aware of.

1. Run the Microservice or Monolithic projects

```bash
# Run the Microservice project with n=2 replicas of the battery management service

cd Microservice
docker compose down -v # Clear the stack, and remove all attached volumes
docker compose up --scale batterymanagement=2 --build

# Run the Monolithic project

cd Monolithic
docker compose down -v
docker compose up --build
```

2. Run the k6s tests

```bash
k6s run loadtest.js # Run in the root directory of the project.
```

## Results
Performing these tests for the Monolithic architecture and the Microservice architecture (n=[1,2,4,8,16,32]) for 3 trials each yields the following results.


