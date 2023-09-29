FROM python:3.10-slim
COPY BatteryManagement/requirements.txt .
RUN pip3 install -r requirements.txt

COPY Common Common
COPY Gateway Gateway
COPY BatteryManagement/*.py .

CMD ["python", "main.py"]