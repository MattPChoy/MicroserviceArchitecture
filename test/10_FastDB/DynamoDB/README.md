# DynamoDB Proof-of-Concept

## Test Setup

1. Run DynamoDB using the following command:

    ```bash
    docker run -p 8000:8000 amazon/dynamodb-local
    ```

2. Install Dependencies

    ```bash
    pip3 install -r requirements.txt
    ```

3. Run the Python script using `python test.py`