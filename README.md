# Take home assessment for Fetch Data Engineer position

## AWS ETL pipeline development 

A small application that can read from an AWS SQS Queue, transform that data, then write to a Postgres database. 

## Project setup and pre-requisites

* GitHub Account -> https://github.com/Thanushri16/Fetch-DataEng-AWS-ETL-Pipeline
* Docker or Docker desktop
* psql
* docker-compose 
* awscli-local

## How to run the Python ETL pipeline application
```
pip install -r requirements.txt
docker-compose up --build
```

## How to test local access of reading message from SQS queue from terminal
```
awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue
```

## How to test local access of Postgres Database from terminal
```
docker-compose exec postgres bash
psql -d postgres -U postgres -p 5432 -h localhost -W
postgres=# \c postgres
postgres=# \d
postgres=# select * from user_logins;
```

## How to stop the Python ETL pipeline application
```
docker-compose down
```