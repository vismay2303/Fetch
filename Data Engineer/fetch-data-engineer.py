import boto3
import json
import logging
import os
import hashlib
import psycopg2
from datetime import datetime

os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'

### CONVERT VERSION TO INTEGER AS PER DDL
def convert_version_int(version):
    if version is not None:
        major, minor, patch = map(int, version.split('.'))
        binary_str = f'{bin(major)[2:]}{bin(minor)[2:]}{bin(patch)[2:]}'
        return int(binary_str, 2)
    else:
        return 0



def getMessages(sqs, queue_url):
    ### RECEIVE MSGS
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=100,
        VisibilityTimeout=0,
        WaitTimeSeconds=0
    )

    return response

def process_response(response):
    ### PARSING JSON RETURED
    records = []
    if 'Messages' in response.keys():
        ### IN CASE OF MULTIPLE MSGS
        for message in response['Messages']:
            message_json_object = json.loads(message['Body'])
            ### LOGGING MESSAGE
            logging.info('Message Body' + str(message_json_object))

            user_id = message_json_object['user_id']
            device_type = message_json_object['device_type']
            locale = message_json_object['locale']
            app_version = message_json_object['app_version']
            ip = message_json_object['ip']
            device_id = message_json_object['device_id']
            # DDL has version number as int
            int_version = convert_version_int(app_version)

            if user_id is None or device_id is None or ip is None or app_version is None:
                logging.info("Invalid Data")
                return None
            # Masking using SHA256
            masked_ip = hashlib.sha256(ip.encode("utf-8")).hexdigest()
            masked_device_id = hashlib.sha256(device_id.encode("utf-8")).hexdigest()
            
            masked_message = {
                'user_id': user_id,
                'device_type': device_type,
                'masked_ip': masked_ip,
                'masked_device_id': masked_device_id,
                'locale': locale,
                'app_version': int_version
            }

            logging.info('Masked Message' + str(masked_message))
            records.append(masked_message)
        return records

    else:
        logging.info('No Messages')
        return None
    


def insert_to_postgres(conn, records):
    with psycopg2.connect(**conn) as connection:
        with connection.cursor() as cur:
            # Insert the record into the user_logins table
            for record in records:
                insert_query = """ INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)  VALUES (%s, %s, %s, %s, %s, %s, NOW());"""
                # Convert to tuple before inserting

                cur.execute(insert_query, (record['user_id'], record['device_type'], record['masked_ip'], record['masked_device_id'], record['locale'], record['app_version']))
            connection.commit()


def main():
    ### AWS CONFIG
    queue_url = 'http://localhost:4566/000000000000/login-queue'
    sqs = boto3.client('sqs', region_name = 'us-east-2', endpoint_url = queue_url)

    ### POSTGRES CONFIG
    pg_conn = {}
    pg_conn['dbname'] = 'postgres'
    pg_conn['user'] ='postgres'
    pg_conn['password'] ='postgres'
    pg_conn['host'] ='localhost'
    pg_conn['port'] ='5432'

    response = getMessages(sqs, queue_url)
    records = process_response(response)
    insert_to_postgres(pg_conn, records)

if __name__ == "__main__":
    main()

