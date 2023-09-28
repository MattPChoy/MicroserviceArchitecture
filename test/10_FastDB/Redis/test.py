import random

from TableManager import Tasks

import uuid
import json
import time
from TableManager import Tasks, TaskStatus

tasksTable = Tasks()

print("Clearing out existing entities in the Redis table.")
for i in tasksTable.redis_client.keys("*"):
    tasksTable.redis_client.delete(i)

t1 = time.time()

n_ops = 10000

sample = None

for i in range(1, n_ops + 1):
    correlation_id = str(uuid.uuid4())

    batt_id = random.randint(1, 1000)
    charge = random.randint(1, 100)
    capacity = random.randint(1, 100)

    data = json.dumps({'data': {'battery_id': batt_id, 'charge': charge, 'capacity': capacity,
                                'iteration': i}})

    if i == n_ops // 2:
        print(correlation_id, data)
        sample = correlation_id
    tasksTable.add(correlation_id=correlation_id)
    tasksTable.update(correlation_id=correlation_id, status=TaskStatus.IN_PROGRESS, payload='{}')

    tasksTable.update(correlation_id=correlation_id, status=TaskStatus.SUCCEEDED,
                      payload=data)

t2 = time.time()
print(f"{len(tasksTable.redis_client.keys('*'))} operations took {t2 - t1}")
print(tasksTable.get(sample))
