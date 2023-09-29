# Data Engineering Project
# ETL off an SQS Queue

## OBJECTIVE: 
- read JSON data containing user login behavior from an AWS SQS Queue, that is made available via a custom localstack image that has the data pre loaded.
- Fetch wants to hide personal identifiable information (PII). The fields `device_id` and `ip` should be masked, but in a way where it is easy for data analysts to identify duplicate values in those fields.
- Once you have flattened the JSON data object and masked those two fields, write each record to a Postgres database that is made available via a custom postgres image that has the tables pre created.

## SETUP

### Requirements
- Python 3.8+
- Docker
- AWS CLI 
- psql 13 or above
- libraries (hashlib, psycopg2, boto3 and other minor ones)

### Installation
Step-by-step instructions are as follows:

1. Clone the repository.
2. Install the required Python packages using `pip`:
    ```
    pip install -r requirements.txt
    ```
3. Set up the local development environment using Docker Compose: 
    ```
    docker-compose up -d
    ```
4. Test local setup using the following steps:
    - Read a message from the queue using `awslocal`:
    ```
    awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
    ```
    - Connect to the PostgreSQL database and verify the table is created:
    ```
    psql -d postgres -U postgres -p 5432 -h localhost -W
    ```
    - Then, run the following SQL command:
    ```
    \dt user_logins
    ```
5. Then, run the following command in another terminal inside the data engineer folder: 
    ```
    python .\fetch-data-engineer.py
    ```
6. Navigate back to the previous terminal and open postgres and run the following command to verify the data: 
    ```
    select * from user_logins
    ```