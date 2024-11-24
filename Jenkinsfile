pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'benl89/todo_app'
        DOCKER_TAG = 'latest'
        // Added new environment variables for monitoring
        MYSQL_EXPORTER_VERSION = '1.0.0'
        PROMETHEUS_VERSION = '2.47.0'
        GRAFANA_VERSION = '10.0.3'
    }
    
    parameters {
        string(
            name: 'DB_HOST',
            defaultValue: 'mysql',
            description: 'Enter the database host address'
        )
        // Added new parameters for monitoring credentials
        string(
            name: 'MYSQL_ROOT_PASSWORD',
            defaultValue: 'password',
            description: 'MySQL root password for monitoring'
        )
    }
    
    stages {
        // Your existing stages remain the same until 'Deploy with Docker Compose'
        stage('Verify Files') {
            steps {
                bat '''
                    echo "Workspace contents:"
                    dir
                    echo "Requirements.txt contents:"
                    type requirements.txt
                '''
            }
        }
        
        stage('Display DB Host') {
            steps {
                script {
                    echo "Database host: ${params.DB_HOST}"
                }
            }
        }
        
        stage('Debug') {
            steps {
                bat 'echo %CD%'
                bat 'dir'
                bat 'git status'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    bat """
                        echo "Building Docker image..."
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} --build-arg DB_HOST=${params.DB_HOST} .
                    """
                }
            }
        }
        
        stage('Login to DockerHub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                    bat 'docker login -u %DOCKERHUB_USERNAME% -p %DOCKERHUB_PASSWORD%'
                }
            }
        }
        
        stage('Push to DockerHub') {
            steps {
                bat "docker push ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }
        
        // Modified the Docker Compose deployment to include monitoring
        stage('Deploy with Docker Compose') {
            steps {
                script {
                    // Create monitoring docker-compose override file
                    writeFile file: 'docker-compose.monitoring.yml', text: '''
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:${PROMETHEUS_VERSION}
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  mysql-exporter:
    image: prom/mysqld-exporter:${MYSQL_EXPORTER_VERSION}
    environment:
      - DATA_SOURCE_NAME=root:${MYSQL_ROOT_PASSWORD}@(${DB_HOST}:3306)/
    ports:
      - "9104:9104"

  grafana:
    image: grafana/grafana:${GRAFANA_VERSION}
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
'''
                    
                    // Create Prometheus config
                    writeFile file: 'prometheus.yml', text: '''
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mysql'
    static_configs:
      - targets: ['mysql-exporter:9104']
  - job_name: 'flask'
    static_configs:
      - targets: ['todo_app:5000']
'''
                    
                    // Deploy everything
                    bat """
                        echo "Deploying with Docker Compose..."
                        set DB_HOST=${params.DB_HOST}
                        set MYSQL_ROOT_PASSWORD=${params.MYSQL_ROOT_PASSWORD}
                        docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
                    """
                }
            }
        }
        
        // Added new stage to verify monitoring setup
        stage('Verify Monitoring') {
            steps {
                script {
                    // Wait for services to be ready
                    bat '''
                        timeout /t 30 /nobreak
                        echo "Checking monitoring services..."
                        docker ps | findstr "prometheus"
                        docker ps | findstr "mysql-exporter"
                        docker ps | findstr "grafana"
                    '''
                }
            }
        }
    }
    
    post {
        always {
            bat 'docker logout'
            bat """
                docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || exit 0
                docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml down || exit 0
            """
        }
    }
}
