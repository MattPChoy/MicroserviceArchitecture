# Use the base python 3.10 image
FROM python:3.10

# Copy the requirements.txt file from the dev directory into the container
COPY requirements.txt .

# Install those dependencies
RUN pip3 install -r requirements.txt

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# Declare the source directory
WORKDIR /usr/src/app/BatteryManagementService

# Copy the sourcecode
COPY BatteryManagementService.py .

# Execute the script
CMD [ "python3", "BatteryManagementService.py" ]