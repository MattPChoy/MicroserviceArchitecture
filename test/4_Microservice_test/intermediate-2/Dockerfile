# basic python image
FROM python:3.10

# install pika to access rabbitmq
RUN pip install pika

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# declare the source directory
WORKDIR /usr/src/app/intermediate-2

# copy the file
COPY intermediate-2.py .

# start command
CMD [ "python", "intermediate-2.py" ]
