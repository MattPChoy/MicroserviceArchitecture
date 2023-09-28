FROM python:3.9

COPY ./app.py /app/app.py
COPY ./requirements.txt /app/requirements.txt
ENV PYTHONUNBUFFERED=1

RUN pip install -r /app/requirements.txt

CMD ["python", "/app/app.py"]
