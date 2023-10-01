FROM python:3.10-slim
ENV PYTHONUNBUFFERED=1
COPY BatteryManagement/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY Common Common
COPY Gateway Gateway
COPY BatteryManagement/*.py .

CMD ["python", "main.py"]
