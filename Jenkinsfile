pipeline {
    agent {
        kubernetes {
            yaml '''
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: helm-kubectl
                    image: dtzar/helm-kubectl
                    command:
                    - cat
                    tty: true
                  - name: docker
                    image: docker:latest
                    command:
                    - cat
                    tty: true
                    volumeMounts:
                    - mountPath: /var/run/docker.sock
                      name: docker-sock
                  volumes:
                  - name: docker-sock
                    hostPath:
                      path: /var/run/docker.sock
            '''
        }
    }
    
    environment {
        DOCKER_REGISTRY = "your-registry"  // Replace with your registry
        DOCKER_IMAGE = "shashkist/flask-contacts-app"
        DOCKER_TAG = "1.4"
        HELM_RELEASE_NAME = "todo-app"
    }
    
    stages {
        stage('Build and Push Docker Image') {
            steps {
                container('docker') {
                    sh '''
                        docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .
                        docker push ${DOCKER_IMAGE}:${DOCKER_TAG}
                    '''
                }
            }
        }
        
        stage('Add Helm Repositories') {
            steps {
                container('helm-kubectl') {
                    sh '''
                        helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
                        helm repo add grafana https://grafana.github.io/helm-charts
                        helm repo update
                    '''
                }
            }
        }
        
        stage('Deploy MySQL') {
            steps {
                container('helm-kubectl') {
                    sh '''
                        # Create MySQL ConfigMap
                        kubectl apply -f kubernetes/mysql/configmap.yaml
                        
                        # Create MySQL Secrets
                        kubectl apply -f kubernetes/mysql/secrets.yaml
                        
                        # Create MySQL PVC
                        kubectl apply -f kubernetes/mysql/pvc.yaml
                        
                        # Deploy MySQL
                        kubectl apply -f kubernetes/mysql/deployment.yaml
                    '''
                }
            }
        }
        
        stage('Install Monitoring Stack') {
            steps {
                container('helm-kubectl') {
                    sh '''
                        # Install Prometheus
                        helm install prometheus prometheus-community/prometheus \
                            -f kubernetes/monitoring/prometheus-values.yaml
                            
                        # Install MySQL Exporter
                        helm install mysql-exporter prometheus-community/prometheus-mysql-exporter \
                            -f kubernetes/monitoring/mysql-exporter-values.yaml
                            
                        # Install Grafana
                        helm install grafana grafana/grafana \
                            -f kubernetes/monitoring/grafana-values.yaml
                            
                        # Apply ServiceMonitor
                        kubectl apply -f kubernetes/monitoring/service-monitor.yaml
                    '''
                }
            }
        }
        
        stage('Deploy Flask Application') {
            steps {
                container('helm-kubectl') {
                    sh '''
                        # Create Flask ConfigMap
                        kubectl apply -f kubernetes/flask/configmap.yaml
                        
                        # Create Flask Secrets
                        kubectl apply -f kubernetes/flask/secrets.yaml
                        
                        # Create Flask PVC
                        kubectl apply -f kubernetes/flask/pvc.yaml
                        
                        # Deploy Flask App
                        kubectl apply -f kubernetes/flask/deployment.yaml
                        
                        # Create Flask Service
                        kubectl apply -f kubernetes/flask/service.yaml
                    '''
                }
            }
        }
        
        stage('Verify Deployments') {
            steps {
                container('helm-kubectl') {
                    sh '''
                        # Wait for MySQL to be ready
                        kubectl rollout status deployment/mysql
                        
                        # Wait for Flask app to be ready
                        kubectl rollout status deployment/flask-app
                        
                        # Check Prometheus targets
                        kubectl get servicemonitors
                        
                        # Get all running pods
                        kubectl get pods
                    '''
                }
            }
        }
    }
    
    post {
        failure {
            echo 'Deployment failed! Starting cleanup...'
            container('helm-kubectl') {
                sh '''
                    helm uninstall mysql-exporter || true
                    helm uninstall prometheus || true
                    helm uninstall grafana || true
                    kubectl delete -f kubernetes/flask/ || true
                    kubectl delete -f kubernetes/mysql/ || true
                    kubectl delete -f kubernetes/monitoring/ || true
                '''
            }
        }
    }
}
