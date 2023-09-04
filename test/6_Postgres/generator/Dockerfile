# basic python image
FROM python:3.10

# install pika to access rabbitmq
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# declare the source directory
WORKDIR /usr/src/app/generator

# copy the file
COPY generator.py .

# start command
CMD [ "python3", "generator.py" ]
