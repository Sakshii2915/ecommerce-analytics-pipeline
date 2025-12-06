# PowerShell Deployment script for E-Commerce Analytics Pipeline
# This script automates the deployment process on Windows

$ErrorActionPreference = "Stop"

# Configuration
$STACK_NAME = "ecommerce-analytics-pipeline"
$PROJECT_NAME = "ecommerce-analytics"
$REGION = if ($env:AWS_DEFAULT_REGION) { $env:AWS_DEFAULT_REGION } else { "us-east-1" }

Write-Host "========================================" -ForegroundColor Green
Write-Host "E-Commerce Analytics Pipeline Deployment" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check AWS CLI
try {
    aws --version | Out-Null
} catch {
    Write-Host "Error: AWS CLI is not installed" -ForegroundColor Red
    exit 1
}

# Check AWS credentials
try {
    aws sts get-caller-identity | Out-Null
} catch {
    Write-Host "Error: AWS credentials not configured" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Creating Glue Scripts S3 Bucket" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$GLUE_SCRIPTS_BUCKET = "${PROJECT_NAME}-glue-scripts-${timestamp}"

try {
    aws s3 mb "s3://${GLUE_SCRIPTS_BUCKET}" --region $REGION 2>&1 | Out-Null
    Write-Host "Created bucket: $GLUE_SCRIPTS_BUCKET" -ForegroundColor Green
} catch {
    Write-Host "Bucket may already exist: $GLUE_SCRIPTS_BUCKET" -ForegroundColor Yellow
}

Write-Host "Step 2: Uploading Glue ETL Script" -ForegroundColor Yellow
aws s3 cp glue/etl-job.py "s3://${GLUE_SCRIPTS_BUCKET}/glue/etl-job.py"
Write-Host "Uploaded Glue script" -ForegroundColor Green

Write-Host "Step 3: Deploying CloudFormation Stack" -ForegroundColor Yellow
$stackExists = $false
try {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION 2>&1 | Out-Null
    $stackExists = $true
} catch {
    $stackExists = $false
}

if ($stackExists) {
    Write-Host "Stack exists, updating..." -ForegroundColor Yellow
    aws cloudformation update-stack `
        --stack-name $STACK_NAME `
        --template-body file://infrastructure/cloudformation-template.yaml `
        --capabilities CAPABILITY_NAMED_IAM `
        --parameters `
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME `
            ParameterKey=RawDataBucketName,ParameterValue="ecommerce-raw-data" `
            ParameterKey=ProcessedDataBucketName,ParameterValue="ecommerce-processed-data" `
        --region $REGION 2>&1 | Out-Null
} else {
    Write-Host "Creating new stack..." -ForegroundColor Yellow
    aws cloudformation create-stack `
        --stack-name $STACK_NAME `
        --template-body file://infrastructure/cloudformation-template.yaml `
        --capabilities CAPABILITY_NAMED_IAM `
        --parameters `
            ParameterKey=ProjectName,ParameterValue=$PROJECT_NAME `
            ParameterKey=RawDataBucketName,ParameterValue="ecommerce-raw-data" `
            ParameterKey=ProcessedDataBucketName,ParameterValue="ecommerce-processed-data" `
        --region $REGION
}

Write-Host "Waiting for stack creation/update..." -ForegroundColor Yellow
if ($stackExists) {
    aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION
} else {
    aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
}

Write-Host "Stack deployment complete!" -ForegroundColor Green

Write-Host "Step 4: Getting stack outputs" -ForegroundColor Yellow
$RAW_BUCKET = aws cloudformation describe-stacks `
    --stack-name $STACK_NAME `
    --region $REGION `
    --query 'Stacks[0].Outputs[?OutputKey==`RawDataBucketName`].OutputValue' `
    --output text

$PROCESSED_BUCKET = aws cloudformation describe-stacks `
    --stack-name $STACK_NAME `
    --region $REGION `
    --query 'Stacks[0].Outputs[?OutputKey==`ProcessedDataBucketName`].OutputValue' `
    --output text

$LAMBDA_FUNCTION = aws cloudformation describe-stacks `
    --stack-name $STACK_NAME `
    --region $REGION `
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' `
    --output text

Write-Host "Raw Data Bucket: $RAW_BUCKET" -ForegroundColor Green
Write-Host "Processed Data Bucket: $PROCESSED_BUCKET" -ForegroundColor Green
Write-Host "Lambda Function: $LAMBDA_FUNCTION" -ForegroundColor Green

Write-Host "Step 5: Updating Lambda function code" -ForegroundColor Yellow
Push-Location lambda
Compress-Archive -Path trigger-glue-job.py -DestinationPath trigger-glue-job.zip -Force

aws lambda update-function-code `
    --function-name $LAMBDA_FUNCTION `
    --zip-file fileb://trigger-glue-job.zip `
    --region $REGION | Out-Null

aws lambda update-function-configuration `
    --function-name $LAMBDA_FUNCTION `
    --environment "Variables={PROCESSED_BUCKET=${PROCESSED_BUCKET}}" `
    --region $REGION | Out-Null

Remove-Item trigger-glue-job.zip -Force
Pop-Location
Write-Host "Lambda function updated" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Generate sample data: python data-generator/generate-sample-data.py"
Write-Host "2. Upload data: aws s3 cp data-generator/output/transactions.csv s3://${RAW_BUCKET}/raw/transactions_$(Get-Date -Format 'yyyyMMdd').csv"
Write-Host "3. Monitor Glue job in AWS Console"
Write-Host "4. Query data in Athena"
Write-Host "5. Set up QuickSight dashboard (see quicksight/dashboard-setup.md)"
Write-Host ""

