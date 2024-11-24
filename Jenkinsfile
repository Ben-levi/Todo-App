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
"""
        }
    }

    environment {
        PROMETHEUS_NS = 'monitoring'
        MYSQL_NS = 'database'
        APP_NS = 'application'
    }

    stages {
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

        stage('Install MySQL') {
            steps {
                container('helm-kubectl') {
                    sh """
                        # Create namespace if it doesn't exist
                        kubectl create namespace ${MYSQL_NS} --dry-run=client -o yaml | kubectl apply -f -
                        
                        # Apply MySQL manifests
                        kubectl apply -f kubernetes/mysql/deployment.yaml -n ${MYSQL_NS}
                        kubectl apply -f kubernetes/mysql/service.yaml -n ${MYSQL_NS}
                        
                        # Wait for MySQL to be ready
                        kubectl wait --for=condition=available deployment -l app=mysql -n ${MYSQL_NS} --timeout=300s
                    """
                }
            }
        }

        stage('Install MySQL Exporter') {
            steps {
                container('helm-kubectl') {
                    sh """
                        # Install MySQL exporter using custom values
                        helm upgrade --install mysql-exporter prometheus-community/prometheus-mysql-exporter \
                            -f kubernetes/monitoring/mysql-exporter-values.yaml \
                            --namespace ${MYSQL_NS} \
                            --wait
                    """
                }
            }
        }

        stage('Install Flask App') {
            steps {
                container('helm-kubectl') {
                    sh """
                        # Create namespace if it doesn't exist
                        kubectl create namespace ${APP_NS} --dry-run=client -o yaml | kubectl apply -f -
                        
                        # Deploy Flask application
                        kubectl apply -f kubernetes/flask/deployment.yaml -n ${APP_NS}
                        kubectl apply -f kubernetes/flask/service.yaml -n ${APP_NS}
                        
                        # Wait for Flask app to be ready
                        kubectl wait --for=condition=available deployment -l app=flask-app -n ${APP_NS} --timeout=300s
                    """
                }
            }
        }

        stage('Configure Service Monitor') {
            steps {
                container('helm-kubectl') {
                    sh """
                        # Apply ServiceMonitor for Flask app
                        kubectl apply -f kubernetes/monitoring/service-monitor.yaml -n ${APP_NS}
                        
                        # Verify ServiceMonitor is created
                        kubectl get servicemonitor -n ${APP_NS}
                    """
                }
            }
        }
    }

    post {
        success {
            echo 'Successfully deployed all components!'
        }
        failure {
            echo 'Pipeline failed! Please check the logs for details.'
        }
    }
}
