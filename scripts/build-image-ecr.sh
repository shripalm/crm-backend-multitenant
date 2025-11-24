#!/bin/bash
set -e

# Usage: ./build_and_push.sh [Dockerfile_name]
# Example: ./build_and_push.sh Dockerfile.dev

# Default Dockerfile
DOCKERFILE=${1:-Dockerfile}

# Ask for AWS region
echo "Select AWS region:"
select REGION_CHOICE in "ap-south-1" "ap-east-1"; do
    case $REGION_CHOICE in
        "ap-south-1")
            AWS_REGION="ap-south-1"
            break
            ;;
        "ap-east-1")
            AWS_REGION="ap-east-1"
            break
            ;;
        *)
            echo "❌ Invalid selection. Please choose 1 or 2."
            ;;
    esac
done

AWS_PROFILE="spark-revamp"
ECR_URL="582054875975.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_NAME="media-spark/unified_backend"

echo "🔹 Using Dockerfile: $DOCKERFILE"
echo "🔹 Selected AWS Region: $AWS_REGION"
echo "🔹 ECR URL: $ECR_URL"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION --profile $AWS_PROFILE | docker login --username AWS --password-stdin $ECR_URL

# Build the image
DOCKER_BUILDKIT=0 docker buildx build --platform linux/amd64 -f $DOCKERFILE -t $IMAGE_NAME .
DOCKER_BUILDKIT=0 docker buildx build --platform linux/amd64 -f $DOCKERFILE -t $IMAGE_NAME --load .

# Tag and push to ECR
docker tag ${IMAGE_NAME}:latest ${ECR_URL}/${IMAGE_NAME}:latest
docker push ${ECR_URL}/${IMAGE_NAME}:latest

echo "✅ Successfully pushed ${ECR_URL}/${IMAGE_NAME}:latest"