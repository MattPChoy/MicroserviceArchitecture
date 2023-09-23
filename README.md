# MicroserviceArchitecture

This GitHub repository contains the source-code for my thesis project. I'm trying to develop and validate the software
architecture for a system that allows consumers to swap their electric vehicle batteries at dedicated "Battery Swap
Stations". The primary goal of the system is to be highly scalable and fault-tolerant so that it can be scaled to handle
a large volume of users.

The source code in this repository is divided as follows:

1. `src/` The main source-code used to validate the software architecture proposed.
2. `test/` This directory contains all intermediate tests used to validate architectural decisions made along the way.

Each test (and the src/ directory itself) should have a README.md document describing the intent of the source-code, as
well as instructions of how to use it. However, to get started, you should install Docker as orchestration of this
source-code uses docker and docker-compose.