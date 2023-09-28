from botocore.exceptions import ClientError
import logging
import boto3
from .TaskStatus import TaskStatus


class Tasks:
    def __init__(self, dyn_resource=None):

        if dyn_resource is None:
            dyn_resource = boto3.resource('dynamodb', region_name='us-east-1')
        self.dyn_resource = dyn_resource
        self.table = None
        self.table_name = 'Tasks'
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(asctime)s: %(message)s")

        self.create_table() if not self.exists() else self.logger.info("Skipping table creation as it already exists")

    def exists(self):
        try:
            table = self.dyn_resource.Table(self.table_name)
            table.load()
            exists = True
        except ClientError as err:
            if err.response['Error']['Code'] == 'ResourceNotFoundException':
                exists = False
            else:
                self.logger.error(f"Couldn't check for the existence of {self.table_name} because "
                                  f"{err.response['Error']['Code']}: {err.response['Error']['Message']}")
                raise
        else:
            self.table = table
        return exists

    def create_table(self):
        try:
            self.table = self.dyn_resource.create_table(
                TableName='Tasks',
                KeySchema=[
                    # KeyType can either be Hash or Range
                    # Hash - just used for indexing
                    # Range - numbers close to each other will beo stored close to each other
                    {'AttributeName': 'correlation_id', 'KeyType': 'HASH'},
                ],
                # AttributeType can be S (string), N (number), B (binary)
                AttributeDefinitions=[
                    {'AttributeName': 'correlation_id', 'AttributeType': 'S'},
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            )
            self.table.wait_until_exists()
        except ClientError as err:
            self.logger.error(f"Couldn't create table Batteries: {err.response['Error']['Code']} : "
                              f"{err.response['Error']['Message']}")
            raise
        else:
            return self.table

    def add_task(self, correlation_id):
        try:
            self.table.put_item(
                Item={
                    'correlation_id': correlation_id,
                    'status': 0,
                    'payload': ''
                }
            )
        except ClientError as err:
            self.logger.error(f"Couldn't add task {correlation_id} to table {err.response['Error']['Code']} : "
                              f"{err.response['Error']['Message']}")
            raise

    def get_task(self, correlation_id):
        try:
            response = self.table.get_item(Key={'correlation_id': correlation_id})
        except ClientError as err:
            self.logger.error(f"Couldn't retrieve task {correlation_id} from table {err.response['Erorr']['Code']} : "
                              f"{err.response['Error']['Message']}")
            raise
        else:
            # Convert the status to it's enumerated type.
            response['Item']['taskStatus'] = TaskStatus(response['Item']['taskStatus'])
            return response['Item']

    def update_task(self, correlation_id, status, payload):
        if type(status) == TaskStatus:
            status = status.value

        try:
            self.table.update_item(
                Key={'correlation_id': correlation_id},
                UpdateExpression='SET taskStatus = :taskStatus, payload = :payload',
                ExpressionAttributeValues={
                    ':taskStatus': status,
                    ':payload': payload
                }
            )
        except ClientError as err:
            self.logger.error(f"Couldn't update task {correlation_id} in table {err.response['Error']['Code']} : "
                              f"{err.response['Error']['Message']}")
            raise

    def delete_task(self, correlation_id):
        try:
            self.table.delete_item(Key={'correlation_id': correlation_id})
        except ClientError as err:
            self.logger.error("Couldn't delete task {correlation_id} from table {err.response['Error']['Code']} : "
                              f"{err.response['Error']['Message']}")
            raise
