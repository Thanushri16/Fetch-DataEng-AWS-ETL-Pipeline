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

## Thought process of developing the solution
- **How will you read messages from the queue?**
  
  Firstly, I thought of running the LocalStack and the Postgres services using docker-compose. To read messages from the SQS queue in LocalStack, I can use the hostname of the LocalStack service to connect to the AWS SQS service using Boto3 (Python SDK for AWS). Once I find the Queue Url, I received messages from the SQS Queue using long polling that allows the receive_messages operation to wait for a specified duration for messages to become available in the queue before returning a response. This approach is advantageous as it contributes to reduced network load and lower latency for message retrieval. This approach is also preferred for real-time message retrieval where once a message is published to the queue, it can be immediately processed. After I receive the messages, I convert them to JSON and then I start processing each message to mask it and load it to the database. After loading the details of each message in the database, I delete the message from the queue. 

- **What type of data structures should be used?**
    
  The data structure that is used primarily for the entire operation of receiving messages, processing and loading them to the postgres database is a Python Dictionary. This is because, all the messages received, processed and stored are being available in JSON object format and Python's Dictionary is the data structure that is best suitable for JSON operations. In addition to this, lists and tuples are also data structures that are being used for message processing and data extraction. 

- **How will you mask the PII data so that duplicate values can be identified?**
  
  The best approach to mask PII data to identify duplicate values in a field is hashing. I have focused on hashing the device_id and the ip of the user's login behavior using the SHA256 hashing algorithm that generates hash values which can be saved in the Postgres table as the masked value. Same input values have the same hash values generated and that way we can find out if there are any duplicate records. 

- **What will be your strategy for connecting and writing to Postgres?**

  My strategy to connect and write to postgres would be to connect to the postgres service running on the docker container in which my python script is also running using the psycopg2.connect function with postgres as the hostname and by entering the credentials of the postgres user. After I connect to the database, I insert each message inside the postgres "user_logins" table and commit the insertion. Once I am done with the process of receiving messages (i.e, when the queue is empty) and inserting them, I close the connection to the postgres database. 

- **Where and how will your application run?**

  The python script (the application) along with the LocalStack and the Postgres services would run within a docker container in the same network. The Dockerfile sets up a Python 3.9 environment, installs the required dependencies from requirements.txt, copies the project files to the container, and sets the command to run the pipeline_app.py Python script.
  
  To run the application, the "docker-compose up --build" command should be executed in the directory containing the docker-compose.yml, Dockerfile, and pipeline_app.py files. This will build the Docker image and start the containers and the application will run inside the docker container to interact with LocalStack and access the queue and its contents using boto3.

## Issues faced in the project execution

I face this issue when I use docker-compose to run the Localstack, Postgres and my python script inside the container. The python application which is running with the Localstack and the postgres services inside of a docker container should use the host names of the Localstack and Postgres services defined in the docker-compose.yml file instead of localhost.  

When I try to access this Localstack service using the Localstack host name with an endpoint url to AWS boto3 SQS service, it connects with the Localstack but it gives an error saying that the SQS login queue doesn't exist! 

However, when I check locally using awslocal command instead of from within a docker container, the queue and the messages in the queue exist. I am able to view the queue and its contents locally but when I run the application inside the docker container, I constantly get the "Queue Does Not Exist" error.

I have performed the following techniques to avoid the error:
* Running all the services (localstack, postgres and the app) inside the same docker container and explicitly mentioning a network that can be common to all of them. 
* Made sure that the app starts running after starting the postgres and the localstack services.
* Setting dummy variables to the app's environment so that the localstack connection wouldn't give an Missing Credentials Error. 
* Used correctly the localstack service name as the boto3 client endpoint url - http://localstack:4566.
* Used the correct Queue URL with the localstack service name - http://localstack:4566/000000000000/login-queue.
* Used the postgres service name as the host for the postgres service correctly.
* Reviewed the docker-compose logs and the container logs for each of the localstack and the postgres services separately and ensured that they are running.

The error persists after performing all of the abovementioned actions to prevent the error from occuring. I used 2 hours of my time to complete the tasks listed in the assessment and 30 minutes on trying to solve the error. If I had the time (more than the mentioned 2 hours to get this assessment done), I would have solved the error to get the application working as expected and would have also focused on accomplishing the tasks mentioned in the next steps. The application would still work right now with the docker-compose command and the code can be reviewed to take a look at my python application.


## Next Steps on the project

- **How would you deploy this application in production?**

  I have already containerized my python application and the dependencies inside of a docker container by creating a docker image. This image can be used easily to ensure that the application can run consistently across different environments in production. A container orchestration tool like Kubernetes can be used to manage, scale and follow node replication for the deployment of the docker containers in the form of images. Also, in terms of production, it is also important that load balancing is being carried out for which AWS ELB can be used. Furthermore, a CI/CD tool such as Jenkins can be used to automate the build, test, and deployment processes.

- **What other components would you want to add to make this production ready?**

  To make this application production ready, a couple of components have to be added. 
  -> Currently, this application is small-scale and it relies on LocalStack that doesn't require AWS credentials or an AWS account for a setup. However, for a large-scale production ready application, it is of utmost importance to have an AWS account set up so that AWS IAM can be used for authentication, authorization and Role-Based Access Control (RBAC).
  -> Security measures can be included such as data validation and data type checks to prevent security attacks from happening such as SQL injection attack. 
  -> Error and exception handling can be enhanced, logging can be achieved and AWS CloudWatch can be used to monitor the application statistics running on AWS cloud. 

- **How can this application scale with a growing dataset.**

  The application can be scaled horizontally by adding more instances of the application to handle increased load. Again, container orchestration tools such as Kubernetes can be used to manage scaling automatically based on predefined metrics (CPU, memory usage, etc.) or using auto-scaling features provided by cloud platforms. If the database becomes a bottleneck, the database can be scaled vertically (increasing resources) or horizontally (sharding, partitioning) based on the specific requirements and workload patterns.

- **How can PII be recovered later on?**

  If PII is masked using hashing, it cannot be recovered later. Hashing is a one-way process, and the original values cannot be derived from the hashed values. To recover PII later, an alternative approach like pseudonymization can be used, where a reversible mapping between original and masked values is maintained using a lookup table or the masked and the original value is stored in the Postgres database.

- **What are the assumptions you made?**

  -> There are no additional security requirements beyond the provided PII data masking functionality.
  -> The application will run on a single instance or a small-scale deployment, rather than a highly distributed or high-availability setup.
  -> The provided Docker images for localstack and Postgres are accessible and contain the required test data and pre-created tables.