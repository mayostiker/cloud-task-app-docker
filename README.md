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
