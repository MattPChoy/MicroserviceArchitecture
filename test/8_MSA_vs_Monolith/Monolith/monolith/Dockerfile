# basic python image
FROM python:3.10

# install pika to access rabbitmq
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Without this setting, Python never prints anything out.
ENV PYTHONUNBUFFERED=1

# declare the source directory
WORKDIR /usr/src/app/monolith

# copy the file
COPY main.py .

# start command
#CMD [ "python3", "main.py" ]
ENTRYPOINT ["gunicorn"]
EXPOSE 5000
CMD ["-w", "2", "-t", "1000", "-b", "0.0.0.0:5000", "wsgi:app"]