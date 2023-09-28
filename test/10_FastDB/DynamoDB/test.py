import uuid
import json
import boto3
from TableManager import Tasks, TaskStatus

tasksTable = Tasks(
    boto3.resource(
        'dynamodb',
        endpoint_url='http://localhost:8000',
        region_name='us-east-1',
        aws_access_key_id='anything',
        aws_secret_access_key='anything',
    )
)


for i in range(1, 100):
    correlation_id = str(uuid.uuid4())
    tasksTable.add_task(correlation_id=correlation_id)
    tasksTable.update_task(correlation_id=correlation_id, status=TaskStatus.IN_PROGRESS, payload='{}')

    tasksTable.update_task(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                           payload=json.dumps(
                               {'data': {'battery_id': 1234, 'charge': 123, 'capacity': 499, 'iteration': i}}))
