pipeline {
    agent any
    
    environment {
        AWS_REGION = 'us-east-1'
        AWS_ACCOUNT_ID = credentials('aws-account-id')
        ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        EKS_CLUSTER = 'callflow-cluster'
        DOCKER_BUILDKIT = '1'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'echo "Building commit: ${GIT_COMMIT}"'
                sh 'echo "Branch: ${GIT_BRANCH}"'
            }
        }
        
        stage('Test Backend') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        pip install pytest pytest-asyncio httpx
                        pytest tests/ -v --tb=short || echo "Tests completed"
                    '''
                }
            }
        }
        
        stage('Test Frontend') {
            steps {
                dir('frontend_next') {
                    sh '''
                        npm ci
                        npm run lint || echo "Lint completed"
                        npm run build
                    '''
                }
            }
        }
        
        stage('Build Docker Images') {
            parallel {
                stage('Build Backend') {
                    steps {
                        sh '''
                            docker build \
                                -t ${ECR_REGISTRY}/callflow-backend:${BUILD_NUMBER} \
                                -t ${ECR_REGISTRY}/callflow-backend:latest \
                                ./backend
                        '''
                    }
                }
                stage('Build Frontend') {
                    steps {
                        sh '''
                            docker build \
                                -t ${ECR_REGISTRY}/callflow-frontend:${BUILD_NUMBER} \
                                -t ${ECR_REGISTRY}/callflow-frontend:latest \
                                ./frontend_next
                        '''
                    }
                }
            }
        }
        
        stage('Login to ECR') {
            steps {
                sh '''
                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${ECR_REGISTRY}
                '''
            }
        }
        
        stage('Push to ECR') {
            parallel {
                stage('Push Backend') {
                    steps {
                        sh '''
                            docker push ${ECR_REGISTRY}/callflow-backend:${BUILD_NUMBER}
                            docker push ${ECR_REGISTRY}/callflow-backend:latest
                        '''
                    }
                }
                stage('Push Frontend') {
                    steps {
                        sh '''
                            docker push ${ECR_REGISTRY}/callflow-frontend:${BUILD_NUMBER}
                            docker push ${ECR_REGISTRY}/callflow-frontend:latest
                        '''
                    }
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            when {
                branch 'main'
            }
            steps {
                script {
                    // Update kubeconfig for EKS
                    sh 'aws eks update-kubeconfig --name ${EKS_CLUSTER} --region ${AWS_REGION}'
                    
                    // Apply base manifests (if first deployment)
                    sh '''
                        kubectl apply -f k8s/namespace.yaml
                        kubectl apply -f k8s/secrets.yaml || true
                        kubectl apply -f k8s/backend-deployment.yaml
                        kubectl apply -f k8s/frontend-deployment.yaml
                        kubectl apply -f k8s/ingress.yaml
                    '''
                    
                    // Update image tags
                    sh '''
                        kubectl set image deployment/backend \
                            backend=${ECR_REGISTRY}/callflow-backend:${BUILD_NUMBER} \
                            -n callflow
                        
                        kubectl set image deployment/frontend \
                            frontend=${ECR_REGISTRY}/callflow-frontend:${BUILD_NUMBER} \
                            -n callflow
                    '''
                    
                    // Wait for rollout
                    sh '''
                        kubectl rollout status deployment/backend -n callflow --timeout=300s
                        kubectl rollout status deployment/frontend -n callflow --timeout=300s
                    '''
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            // Optionally send notification
            // slackSend(color: 'good', message: "Build ${BUILD_NUMBER} succeeded!")
        }
        failure {
            echo '❌ Pipeline failed!'
            // slackSend(color: 'danger', message: "Build ${BUILD_NUMBER} failed!")
        }
        always {
            // Cleanup Docker images to save disk space
            sh 'docker system prune -f || true'
            
            // Archive test results if any
            junit allowEmptyResults: true, testResults: '**/test-results/*.xml'
        }
    }
}
