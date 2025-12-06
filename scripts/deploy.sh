#!/bin/bash

# Deployment script for E-Commerce Analytics Pipeline
# This script automates the deployment process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
STACK_NAME="ecommerce-analytics-pipeline"
PROJECT_NAME="ecommerce-analytics"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}E-Commerce Analytics Pipeline Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Creating Glue Scripts S3 Bucket${NC}"
GLUE_SCRIPTS_BUCKET="${PROJECT_NAME}-glue-scripts-$(date +%s)"
if aws s3 ls "s3://${GLUE_SCRIPTS_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://${GLUE_SCRIPTS_BUCKET}" --region "${REGION}"
    echo -e "${GREEN}Created bucket: ${GLUE_SCRIPTS_BUCKET}${NC}"
else
    echo -e "${YELLOW}Bucket already exists: ${GLUE_SCRIPTS_BUCKET}${NC}"
fi

echo -e "${YELLOW}Step 2: Uploading Glue ETL Script${NC}"
aws s3 cp glue/etl-job.py "s3://${GLUE_SCRIPTS_BUCKET}/glue/etl-job.py"
echo -e "${GREEN}Uploaded Glue script${NC}"

echo -e "${YELLOW}Step 3: Deploying CloudFormation Stack${NC}"
if aws cloudformation describe-stacks --stack-name "${STACK_NAME}" --region "${REGION}" &> /dev/null; then
    echo -e "${YELLOW}Stack exists, updating...${NC}"
    aws cloudformation update-stack \
        --stack-name "${STACK_NAME}" \
        --template-body file://infrastructure/cloudformation-template.yaml \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameters \
            ParameterKey=ProjectName,ParameterValue="${PROJECT_NAME}" \
            ParameterKey=RawDataBucketName,ParameterValue="ecommerce-raw-data" \
            ParameterKey=ProcessedDataBucketName,ParameterValue="ecommerce-processed-data" \
        --region "${REGION}" || echo -e "${YELLOW}No updates to stack${NC}"
else
    echo -e "${YELLOW}Creating new stack...${NC}"
    aws cloudformation create-stack \
        --stack-name "${STACK_NAME}" \
        --template-body file://infrastructure/cloudformation-template.yaml \
        --capabilities CAPABILITY_NAMED_IAM \
        --parameters \
            ParameterKey=ProjectName,ParameterValue="${PROJECT_NAME}" \
            ParameterKey=RawDataBucketName,ParameterValue="ecommerce-raw-data" \
            ParameterKey=ProcessedDataBucketName,ParameterValue="ecommerce-processed-data" \
        --region "${REGION}"
fi

echo -e "${YELLOW}Waiting for stack creation/update...${NC}"
aws cloudformation wait stack-create-complete --stack-name "${STACK_NAME}" --region "${REGION}" 2>/dev/null || \
aws cloudformation wait stack-update-complete --stack-name "${STACK_NAME}" --region "${REGION}" 2>/dev/null

echo -e "${GREEN}Stack deployment complete!${NC}"

echo -e "${YELLOW}Step 4: Getting stack outputs${NC}"
RAW_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query 'Stacks[0].Outputs[?OutputKey==`RawDataBucketName`].OutputValue' \
    --output text)

PROCESSED_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query 'Stacks[0].Outputs[?OutputKey==`ProcessedDataBucketName`].OutputValue' \
    --output text)

LAMBDA_FUNCTION=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${REGION}" \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
    --output text)

echo -e "${GREEN}Raw Data Bucket: ${RAW_BUCKET}${NC}"
echo -e "${GREEN}Processed Data Bucket: ${PROCESSED_BUCKET}${NC}"
echo -e "${GREEN}Lambda Function: ${LAMBDA_FUNCTION}${NC}"

echo -e "${YELLOW}Step 5: Updating Lambda function code${NC}"
cd lambda
zip -q trigger-glue-job.zip trigger-glue-job.py 2>/dev/null || \
    python -m zipfile -c trigger-glue-job.zip trigger-glue-job.py

aws lambda update-function-code \
    --function-name "${LAMBDA_FUNCTION}" \
    --zip-file fileb://trigger-glue-job.zip \
    --region "${REGION}" > /dev/null

aws lambda update-function-configuration \
    --function-name "${LAMBDA_FUNCTION}" \
    --environment "Variables={PROCESSED_BUCKET=${PROCESSED_BUCKET}}" \
    --region "${REGION}" > /dev/null

rm -f trigger-glue-job.zip
cd ..
echo -e "${GREEN}Lambda function updated${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Generate sample data: python data-generator/generate-sample-data.py"
echo "2. Upload data: aws s3 cp data-generator/output/transactions.csv s3://${RAW_BUCKET}/raw/transactions_\$(date +%Y%m%d).csv"
echo "3. Monitor Glue job in AWS Console"
echo "4. Query data in Athena"
echo "5. Set up QuickSight dashboard (see quicksight/dashboard-setup.md)"
echo ""
echo "Stack outputs saved. Use these values for configuration."

