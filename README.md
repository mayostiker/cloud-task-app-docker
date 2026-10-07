# Cloud Task App – Docker & Containerization

## Project Overview

The Cloud Task App is a simple task management web application built with Python Flask and MySQL.

As part of Module 4 of my Cloud Computing & DevOps internship, I containerized the application using Docker and Docker Compose.

The project demonstrates how a web application and its database can run as separate containers while communicating through a Docker network and storing database data in a persistent Docker volume.

---

## Architecture

```text
                    Browser
                       |
                       | HTTP :5000
                       v
             +----------------------+
             | Flask Web Container  |
             | Python + Flask       |
             | Gunicorn             |
             +----------+-----------+
                        |
                  Docker Network
                        |
                        v
             +----------------------+
             | MySQL 8.4 Container  |
             | Database: taskapp    |
             +----------+-----------+
                        |
                        v
             +----------------------+
             | Docker Named Volume  |
             | mysql_data            |
             +----------------------+
Application Flow
1. A user accesses the application through the browser.
2. Docker maps host port 5000 to the Flask container.
3. Gunicorn serves the Flask application.
4. The Flask container communicates with MySQL through the Docker network.
5. The MySQL database stores task information.
6. A Docker named volume provides persistent database storage.
The Flask application connects to MySQL using the Docker Compose service name:
DB_HOST=db

rather than localhost.
Technologies Used
- Python 3.12
- Flask 3.1.3
- Gunicorn 23.0.0
- MySQL 8.4
- Docker
- Docker Compose
- Docker Volumes
- Docker Networking
- Linux / WSL Ubuntu
- Git / GitHub
Project Structure
cloud-task-app/
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── init.sql
├── requirements.txt
├── app.py
├── database.py
├── static/
│   └── style.css
├── templates/
│   └── index.html
└── README.md

The .env file containing local database credentials is intentionally excluded from Git.

Dockerfile
The application uses a lightweight Python image:
FROM python:3.12-slim

The Dockerfile was optimized by:
- Using the slim Python base image
- Disabling Python bytecode generation
- Enabling unbuffered Python output
- Installing dependencies without retaining pip cache
- Running the application as a non-root user
- Using Gunicorn instead of Flask's development server
- Exposing port 5000
Docker Compose
Docker Compose manages two services:
Web Service
The web service builds the Flask application image and exposes port 5000.
Database Service
The db service runs MySQL 8.4.
The two services communicate through the Docker Compose network.
The application uses:
DB_HOST=db
DB_PORT=3306

The db service name is used as the hostname because Docker Compose provides service-name-based networking.
Environment Variables
Database configuration is supplied through environment variables.
Example:
MYSQL_DATABASE=taskapp
MYSQL_USER=taskadmin
MYSQL_PASSWORD=your_app_password_here
MYSQL_ROOT_PASSWORD=your_root_password_here

The real .env file is excluded from Git using .gitignore.
A .env.example file is provided as a template.
Database Initialization
The init.sql file automatically creates the tasks table when the MySQL database is initialized.
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

Persistent Storage
A Docker named volume is used:
mysql_data

The volume is mounted to:
/var/lib/mysql

This allows database data to persist when the MySQL container is restarted or recreated.
Persistence was tested by restarting the MySQL container and confirming that previously stored tasks remained available.
Running the Application
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd cloud-task-app

2. Create the environment file
Create a .env file based on .env.example:
cp .env.example .env

Update the values with your own database credentials.
3. Start the application
docker compose up --build

4. Open the application
Visit:
http://localhost:5000

Useful Docker Commands
Check running containers:
docker ps

Check all containers:
docker ps -a

Build the application:
docker compose build

Start the application:
docker compose up

Run in detached mode:
docker compose up -d

Stop the application:
docker compose down

View Docker volumes:
docker volume ls

View application logs:
docker compose logs web

Security Considerations
- Database credentials are stored in .env.
- .env is excluded from Git using .gitignore.
- .env.example contains placeholders rather than real credentials.
- The Flask application runs as a non-root appuser inside the container.
- The application uses Gunicorn rather than Flask's development server.
- The MySQL database is not directly published to the host.
Learning Outcomes
Through this project, I gained practical experience with:
- Docker architecture
- Containers and images
- Dockerfiles
- Docker image optimization
- Docker networking
- Environment variables
- Docker volumes
- Persistent database storage
- Docker Compose
- Multi-container applications
- MySQL containerization
- Gunicorn
- Running containers as a non-root user
Internship Module
Module 4 – Docker & Containerization
Cloud Computing & DevOps Internship
Codomax Digital Solutions

---

# Module 5 – DevOps, CI/CD & Monitoring

## Project Overview

As part of Module 5 of my Cloud Computing & DevOps internship, I implemented a CI/CD pipeline for the Cloud Task App.

The pipeline automates application testing, Docker image building, publishing to Amazon ECR, deployment to Amazon EC2, and basic monitoring with Amazon CloudWatch.

---

## CI/CD Architecture

```text
GitHub
   |
   v
GitHub Actions
   |
   +--> Automated Tests
   |
   +--> Docker Build
   |
   v
Amazon ECR
   |
   v
AWS Systems Manager
   |
   v
Amazon EC2
   |
   +--> Flask Container
   |
   +--> MySQL Container
   |
   v
Amazon CloudWatch
   |
   +--> Metrics
   +--> Application Logs
CI/CD Pipeline
The GitHub Actions pipeline performs the following:
1. Code is pushed to the main branch.
2. GitHub Actions installs the Python dependencies.
3. Automated tests are executed with pytest.
4. GitHub Actions authenticates with AWS using GitHub OIDC and IAM.
5. The Docker image is built.
6. The image is tagged using the Git commit SHA and latest.
7. The image is pushed to Amazon ECR.
8. AWS Systems Manager sends a deployment command to EC2.
9. EC2 authenticates with ECR and pulls the new image.
10. Docker Compose recreates the Flask web container.
11. The MySQL container continues using persistent Docker storage.
12. CloudWatch collects infrastructure metrics and application logs.
Automated Testing
Two automated tests were added using pytest.
The tests verify:
- The application home page loads successfully.
- Tasks are displayed correctly.
- New tasks can be submitted.
- The database insert operation is called correctly.
- Expected HTTP responses are returned.
Local test result:
tests/test_app.py::test_home_page PASSED
tests/test_app.py::test_add_task PASSED

2 passed

These tests also run automatically in GitHub Actions.
GitHub Actions
The workflow is stored at:
.github/workflows/ci.yml

The workflow contains two jobs:
Test and Build
- Checkout source code
- Set up Python 3.12
- Install dependencies
- Run pytest
- Authenticate with AWS
- Login to Amazon ECR
- Build the Docker image
- Push the image to ECR
Deploy
The deployment job runs after the test-and-build job succeeds.
It uses the deployment script:
scripts/deploy.sh

The script uses AWS Systems Manager to deploy the Docker image to the EC2 instance.
AWS Authentication
GitHub Actions uses GitHub OpenID Connect (OIDC) to authenticate with AWS.
The workflow assumes the IAM role:
GitHubActionsCloudTaskAppRole

This avoids storing long-lived AWS access keys in GitHub.
The role provides permissions for:
- Amazon ECR image publishing
- AWS Systems Manager deployment
The OIDC trust policy restricts access to the intended GitHub repository and branch.
Amazon ECR
Amazon ECR is used as the private Docker image registry.
Repository:
cloud-task-app

Images are tagged with:
latest
<Git commit SHA>

Using the Git commit SHA allows a deployed image to be associated with a specific source-code version.
Amazon EC2 Deployment
The application runs on an Amazon EC2 t3.micro instance using Amazon Linux 2023.
The EC2 instance uses the IAM role:
Module5EC2Role

The role provides access to:
- Amazon ECR
- AWS Systems Manager
- CloudWatch Agent
The application is deployed under:
/opt/cloud-task-app

Docker Compose runs the Flask application and MySQL database as separate containers.
Production Docker Compose
The production configuration is:
docker-compose.prod.yml

The web container uses the Docker image stored in Amazon ECR.
Gunicorn serves Flask on port 5000 inside the container.
The EC2 instance maps:
EC2 port 80 → Container port 5000

MySQL 8.4 runs as a separate container and uses the persistent Docker volume:
mysql_data

The MySQL database is not directly exposed to the internet.
Automated Deployment
The deployment script:
scripts/deploy.sh

performs the following:
1. Receives the Git commit SHA.
2. Sends a command to EC2 using AWS Systems Manager.
3. Updates the image tag.
4. Logs in to Amazon ECR.
5. Pulls the specified image.
6. Recreates the web container.
7. Keeps the database container running.
8. Removes unused Docker images.
A successful GitHub Actions pipeline therefore automatically deploys the new application version.
Monitoring with Amazon CloudWatch
Amazon CloudWatch provides basic infrastructure and application monitoring.
The CloudWatch Agent runs on the EC2 instance.
Metrics
Custom namespace:
Module5/CloudTaskApp

The following metrics are collected:
- CPU usage
- Memory usage
- Disk usage
Application Logs
Docker application logs are forwarded to:
/module5/cloud-task-app

The log stream identifies the EC2 instance and application.
This provides centralized application logging through CloudWatch.
Environment Variables and Secrets
Sensitive database credentials are not stored in the GitHub repository.
The EC2 production environment uses an .env file containing:
MYSQL_DATABASE
MYSQL_USER
MYSQL_PASSWORD
MYSQL_ROOT_PASSWORD

The .env file is excluded from Git.
The repository contains .env.example with placeholder values.
Security Considerations
The project uses several security practices:
- GitHub OIDC instead of long-lived AWS access keys
- IAM roles for GitHub Actions and EC2
- Restricted GitHub OIDC trust policy
- Database credentials excluded from Git
- .env excluded using .gitignore
- Flask application running as a non-root Docker user
- MySQL not directly exposed to the internet
- EC2 deployment through AWS Systems Manager
- Separate IAM permissions for GitHub Actions and EC2
Technologies Used
Application
- Python 3.12
- Flask 3.1.3
- Gunicorn 23.0.0
- MySQL 8.4
Containerization
- Docker
- Docker Compose
CI/CD
- Git
- GitHub
- GitHub Actions
- pytest
AWS
- Amazon EC2
- Amazon ECR
- AWS IAM
- AWS Systems Manager
- Amazon CloudWatch
- Amazon VPC
Operating System
- Amazon Linux 2023
- Ubuntu / WSL2
Learning Outcomes
Through this module, I gained practical experience with:
- DevOps principles
- Git and GitHub workflows
- Continuous Integration
- Continuous Deployment
- Automated testing with pytest
- GitHub Actions
- GitHub OIDC authentication
- AWS IAM roles and policies
- Docker image automation
- Amazon ECR
- EC2 deployment automation
- AWS Systems Manager
- Docker Compose in a production environment
- CloudWatch metrics
- CloudWatch application logs
- Environment management
- Basic observability
- Infrastructure and application monitoring
Internship Module
Module 5 – DevOps, CI/CD & Monitoring
Cloud Computing & DevOps Internship
Codomax Digital Solutions
