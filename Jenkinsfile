pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'benl89/todo_app'
        DOCKER_TAG = 'latest'
    }

    parameters {
        string(
            name: 'DB_HOST',
            defaultValue: 'mysql',
            description: 'Enter the database host address'
        )
    }

    stages {
        stage('Verify Files') {
            steps {
                // Debug step to verify files are present
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
                    // Build the Docker image with DB_HOST as a build argument
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

        stage('Deploy with Docker Compose') {
            steps {
                script {
                    // Pass DB_HOST as an environment variable to Docker Compose
                    bat """
                        echo "Deploying with Docker Compose..."
                        set DB_HOST=${params.DB_HOST}
                        docker-compose up -d
                    """
                }
            }
        }
    }

    post {
        always {
            bat 'docker logout'
            // Clean up images
            bat "docker rmi ${DOCKER_IMAGE}:${DOCKER_TAG} || exit 0"
        }
    }
}
