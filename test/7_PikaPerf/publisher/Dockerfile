# basic python image
FROM python:3.10

# install pika to access rabbitmq
RUN pip3 install pika

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# declare the source directory
WORKDIR /usr/src/app/publisher

# copy the file
COPY publisher.py .

# start command
CMD [ "python3", "publisher.py" ]
