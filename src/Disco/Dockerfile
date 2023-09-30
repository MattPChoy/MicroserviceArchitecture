FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
COPY Disco/requirements.txt .
RUN pip3 install -r requirements.txt

COPY Common Common
COPY Gateway Gateway
COPY Disco/*.py .

CMD ["python", "main.py"]