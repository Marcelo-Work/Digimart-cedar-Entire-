#!/bin/bash
set -e

REGION="us-east-1"
ACCOUNT_ID="ACCOUNT_ID"
ECR_REGISTRY="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

echo "🔐 Authenticating to ECR..."
aws ecr get-login-password --region $REGION | \
docker login --username AWS --password-stdin $ECR_REGISTRY

create_ecr_repo_if_not_exists() {
    REPO_NAME=$1
    if ! aws ecr describe-repositories --repository-names $REPO_NAME --region $REGION &> /dev/null; then
        echo "📦 Creating ECR repository: $REPO_NAME"
        aws ecr create-repository \
            --repository-name $REPO_NAME \
            --region $REGION \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
    else
        echo "✅ Repository exists: $REPO_NAME"
    fi
}

create_ecr_repo_if_not_exists "digimart-backend"
create_ecr_repo_if_not_exists "digimart-frontend-prod"

echo "🔨 Building backend image..."
cd base-app/src/backend
docker build -t digimart-backend:latest .
docker tag digimart-backend:latest ${ECR_REGISTRY}/digimart-backend:latest
docker push ${ECR_REGISTRY}/digimart-backend:latest
cd ../../..

echo "🔨 Building frontend image..."
cd base-app
docker build -f src/frontend/Dockerfile.ecs -t digimart-frontend-prod:latest .
docker tag digimart-frontend-prod:latest ${ECR_REGISTRY}/digimart-frontend-prod:latest
docker push ${ECR_REGISTRY}/digimart-frontend-prod:latest
cd ..

echo "✅ All images pushed successfully!"
