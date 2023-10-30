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

# Web UI
A small web user interface has been implemented, and is available in the [web](./web) directory. To get started, install `npm` and run the following commands:

```bash
# In the directory containing package.json, install the nodejs dependencies
npm i 
# Use Vite to run the webapp
npm run dev
```


