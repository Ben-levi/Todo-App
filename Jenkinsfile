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
        pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: jenkins-agent
spec:
  containers:
  - name: helm-kubectl
    image: dtzar/helm-kubectl:latest
    command:
    - cat
    tty: true
    volumeMounts:
    - name: kubeconfig
      mountPath: /root/.kube/
  volumes:
  - name: kubeconfig
    secret:
      secretName: kubeconfig
"""
        }
    }

    environment {
        // Define versions and namespaces
        PROMETHEUS_NS = 'monitoring'
        MYSQL_NS = 'database'
        APP_NS = 'application'
    }

    stages {
        stage('Create Namespaces') {
            steps {
                container('helm-kubectl') {
                    sh """
                        kubectl create namespace ${PROMETHEUS_NS} --dry-run=client -o yaml | kubectl apply -f -
                        kubectl create namespace ${MYSQL_NS} --dry-run=client -o yaml | kubectl apply -f -
                        kubectl create namespace ${APP_NS} --dry-run=client -o yaml | kubectl apply -f -
                    """
                }
            }
        }

        stage('Install Prometheus') {
            steps {
                container('helm-kubectl') {
                    sh """
                        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
                        helm repo update
                        helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
                            --namespace ${PROMETHEUS_NS} \
                            --create-namespace \
                            --wait
                    """
                }
            }
        }

        stage('Deploy MySQL') {
            steps {
                container('helm-kubectl') {
                    sh """
                        kubectl apply -f kubernetes/mysql/deployment.yaml -n ${MYSQL_NS}
                        kubectl apply -f kubernetes/mysql/service.yaml -n ${MYSQL_NS}
                        kubectl wait --for=condition=available deployment -l app=mysql -n ${MYSQL_NS} --timeout=300s
                    """
                }
            }
        }

        stage('Install MySQL Exporter') {
            steps {
                container('helm-kubectl') {
                    sh """
                        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
                        helm repo update
                        helm upgrade --install mysql-exporter prometheus-community/prometheus-mysql-exporter \
                            -f kubernetes/monitoring/mysql-exporter-values.yaml \
                            --namespace ${MYSQL_NS} \
                            --wait
                    """
                }
            }
        }

        stage('Deploy Flask App') {
            steps {
                container('helm-kubectl') {
                    sh """
                        kubectl apply -f kubernetes/flask/deployment.yaml -n ${APP_NS}
                        kubectl apply -f kubernetes/flask/service.yaml -n ${APP_NS}
                        kubectl wait --for=condition=available deployment -l app=flask-app -n ${APP_NS} --timeout=300s
                    """
                }
            }
        }

        stage('Configure Monitoring') {
            steps {
                container('helm-kubectl') {
                    sh """
                        # Apply ServiceMonitor for Flask app
                        kubectl apply -f kubernetes/monitoring/service-monitor.yaml -n ${APP_NS}
                        
                        # Verify ServiceMonitor is picked up
                        kubectl get servicemonitor -n ${APP_NS}
                    """
                }
            }
        }
    }

    post {
        always {
            echo 'Pipeline completed'
        }
        success {
            echo 'Successfully deployed all components'
        }
        failure {
            echo 'Pipeline failed'
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
