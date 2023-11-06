# Implementation Source
> This is the root folder of the software architecture implementation for this thesis project.

The software architecture proposed divides up the program into a series of services, 
each of which have their own subdirectory, and a corresponding Dockerfile specifying 
how Docker should build the image.

The services that were implemented and their corresponding directories are:
- [Authentication](./Authentication): This service is responsible for providing the mechanism by which user credentials or tokens are validated by the API Gateway.
- [BatteryManagement](./BatteryManagement): This service is responsible for providing the functionality associated to the management of battery location, state, and battery swapping.
- [Gateway](./Gateway): This service is responsible for processing HTTP requests, translating them into messages onto the message bus and querying services for responses.
- [UserManagement](./UserManagement): This service is responsible for storing and manipulating user records.
- [Discovery](./Disco): This service is responsible for keeping a record of all alive services.

# Codebase Structure
- Within the [Gateway](./Gateway) directory lies two key subdirectories:
  - The [models](./Gateway/models) directory contains all data models used to represent concepts within the system. 
    - Each concept has a Pydantic object used for FastAPI attribute validation, and a corresponding Table class which abstracts the connection to the respective database implementation
  - The [views](./Gateway/views) directory contains the FastAPI Routers that are responsible for routing requests, and awaiting the responses from individual microservices.
- The [Common](./Common) directory defines behaviour that is used through all system subdomains.
  - It provides a single-source-of-truth for how microservices should interact with the message bus through the [BusClient](./Common/BusClient.py) as well as a common framework for how all the microservices are implemented through the [Microservice](./Common/Microservice.py) class. 
# Load Testing
To perform load testing on the software architecture, [k6](https://k6.io/) was used. The primary test script used for
the load testing of the system is [variedLoad.js](./variedLoad.js). The script can be run as follows:

```bash
k6 run variedLoad.js
```

The script can be modified such that the number of VUs for each endpoint, and the ratio of read/write requests can 
be modified at the top of the script.

```js
// % of read requests
const readMult = 0.70;
// Number of Virtual Users for each endpoint
const battery = 400;
const user = 200;
const status = 100;
// Duration of the test.
const duration = "2m";
```

The [constantLoad](./constantLoad.js) script was used in the request duration test, to modulate the throughput volume.

```bash

# Web UI
A small web user interface has been implemented, and is available in the [web](./web) directory. To get started, install `npm` and run the following commands:

```bash
# In the directory containing package.json, install the nodejs dependencies
npm i 
# Use Vite to run the webapp
npm run dev
```


