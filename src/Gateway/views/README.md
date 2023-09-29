# Views
Each microservice that requires routing from the API Gateway should create a Python file here, specifying how 
the requests should be routed to it, and what endpoints are valid. This file should define a FastAPI router which will
be imported and registered in the ../main.py file which is the entrypoint for the API Gateway.