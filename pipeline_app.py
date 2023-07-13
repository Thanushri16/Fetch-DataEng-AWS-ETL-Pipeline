from datetime import date
from configparser import ConfigParser
import hashlib
import json
import os
import sys
import logging
import boto3
import psycopg2

# Read the configuration file
config = ConfigParser(os.environ)
config.read('pipeline_config.ini')
logging.getLogger().setLevel(logging.INFO)


def mask_value(value):
    """Function that masks the input value."""
    return hashlib.sha256(value.encode()).hexdigest()

def database_connect():
    """Function that connects to the postgres database and returns the connection object."""
    try:
        conn = psycopg2.connect(database=config['postgres']['database'],
                                user=config['postgres']['user'],
                                password=config['postgres']['password'],
                                host=config['postgres']['host'],
                                port=config['postgres']['port'])
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"Unable to connect to PostgreSQL database: {e}")
        sys.exit()

def process_message(message):
    """Function that processes the SQS message and loads it into the database."""

    try:
        # Parse the message body received of type string to type json
        message_body = message.body
        data = json.loads(message_body)

    except json.JSONDecodeError as e:
        logging.error(f'Error while parsing JSON: {e}')

    except Exception as e:
        logging.error(f'An unexceptional error occurred \
                      while reading data from the messages in the Queue! {e}')

    try:
        # Connect to the postgres database in the postgres service
        connection = database_connect()
        cursor = connection.cursor()

        # Insert details inside the postgres table
        query = """INSERT INTO USER_LOGINS(user_id, device_type, masked_ip, 
                    masked_device_id, locale, app_version, create_date) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        params = (
                    data['user_id'],
                    data['device_type'],
                    mask_value(data['ip']),
                    mask_value(data['device_id']),
                    data['locale'],
                    data['app_version'],
                    date.today(),
                )
        cursor.execute(query, params)
        connection.commit()
        cursor.close()
        connection.close()

    except (Exception, psycopg2.DatabaseError) as e:
        logging.error(f"Error in updating user's login behavior data to PostgreSQL database: {e}")


def main():
    """Function that performs the main execution."""
    try:
        # Connect to the SQS queue in localstack
        sqs = boto3.resource('sqs', endpoint_url= config['localstack']['LocalStackUrl'])
        queue = sqs.Queue(config['localstack']['QueueUrl'])
        
        # Poll the message queue in a loop
        while True:

            # Read a message from the queue using long polling
            try:
                messages = queue.receive_messages(
                    MaxNumberOfMessages=int(config['localstack']['AwsSqsMaxNumberOfMessages']),
                    WaitTimeSeconds=int(config['localstack']['AwsSqsWaitTimeSeconds'])
                )
            except Exception as e:
                logging.error(f"Error in receiving messages from the queue: {e}")

            if len(messages) == 0:
                break

            for message in messages:
                process_message(message)

                # Delete the message after processing
                try:
                    message.delete()
                except Exception as e:
                    logging.error(f"Error in deleting messages from the queue: {e}")
     
        logging.info("ETL completed!")

    # Exception handling to catch an error when the SQS Queue does not exist
    except (sqs.meta.client.exceptions.QueueDoesNotExist, \
            sqs.meta.client.exceptions.QueueDeletedRecently) as e:
        logging.error(f"SQS Queue does not exist! {e}")
        sys.exit()
    
    except Exception as e:
        logging.error(f"Error in connecting to the Queue URL or SQS Queue does not exist! {e}")
        sys.exit()

if __name__ == "__main__":
    main()
