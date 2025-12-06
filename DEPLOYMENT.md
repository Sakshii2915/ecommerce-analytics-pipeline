# Deployment Guide

This guide provides step-by-step instructions for deploying the serverless e-commerce analytics pipeline.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
   ```bash
   aws configure
   ```
3. **Python 3.8+** installed
4. **boto3** library installed
   ```bash
   pip install -r requirements.txt
   ```

## Step 1: Prepare AWS Environment

### 1.1 Verify AWS CLI Configuration

```bash
aws sts get-caller-identity
```

This should return your AWS account ID and user ARN.

### 1.2 Set AWS Region

```bash
export AWS_DEFAULT_REGION=us-east-1  # or your preferred region
```

## Step 2: Upload Glue ETL Script to S3

The CloudFormation template expects the Glue script to be in S3. We'll create a bucket and upload it.

```bash
# Create a bucket for Glue scripts (replace with unique name)
GLUE_SCRIPTS_BUCKET="ecommerce-glue-scripts-$(date +%s)"

aws s3 mb s3://$GLUE_SCRIPTS_BUCKET

# Upload the ETL script
aws s3 cp glue/etl-job.py s3://$GLUE_SCRIPTS_BUCKET/glue/etl-job.py

# Note the bucket name - you'll need it for CloudFormation
echo "Glue scripts bucket: $GLUE_SCRIPTS_BUCKET"
```

## Step 3: Update CloudFormation Template

Before deploying, update the CloudFormation template to reference your Glue scripts bucket.

Edit `infrastructure/cloudformation-template.yaml` and update the `GlueETLJob` resource's `ScriptLocation`:

```yaml
ScriptLocation: !Sub 's3://${GlueScriptsBucket}/glue/etl-job.py'
```

Or manually set it in the template parameters.

## Step 4: Deploy Infrastructure

### 4.1 Deploy CloudFormation Stack

```bash
aws cloudformation create-stack \
  --stack-name ecommerce-analytics-pipeline \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters \
    ParameterKey=ProjectName,ParameterValue=ecommerce-analytics \
    ParameterKey=RawDataBucketName,ParameterValue=ecommerce-raw-data \
    ParameterKey=ProcessedDataBucketName,ParameterValue=ecommerce-processed-data \
  --region $AWS_DEFAULT_REGION
```

### 4.2 Wait for Stack Creation

```bash
aws cloudformation wait stack-create-complete \
  --stack-name ecommerce-analytics-pipeline
```

### 4.3 Get Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs'
```

Save the output values:
- `RawDataBucketName`
- `ProcessedDataBucketName`
- `GlueJobName`
- `GlueDatabaseName`

## Step 5: Update Lambda Function Code

The CloudFormation template creates a Lambda function with inline code. For production, upload the Lambda function code:

```bash
# Package Lambda function
cd lambda
zip trigger-glue-job.zip trigger-glue-job.py

# Get Lambda function name from stack outputs
LAMBDA_FUNCTION_NAME=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
  --output text)

# Update Lambda function code
aws lambda update-function-code \
  --function-name $LAMBDA_FUNCTION_NAME \
  --zip-file fileb://trigger-glue-job.zip

# Update environment variables
PROCESSED_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`ProcessedDataBucketName`].OutputValue' \
  --output text)

aws lambda update-function-configuration \
  --function-name $LAMBDA_FUNCTION_NAME \
  --environment Variables="{PROCESSED_BUCKET=$PROCESSED_BUCKET}"

cd ..
```

## Step 6: Generate and Upload Sample Data

### 6.1 Generate Sample Data

```bash
cd data-generator
python generate-sample-data.py
cd ..
```

### 6.2 Upload to S3

```bash
# Get raw data bucket name
RAW_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`RawDataBucketName`].OutputValue' \
  --output text)

# Upload sample data (this will trigger the Lambda and Glue job)
aws s3 cp data-generator/output/transactions.csv \
  s3://$RAW_BUCKET/raw/transactions_$(date +%Y%m%d_%H%M%S).csv
```

## Step 7: Monitor Glue Job Execution

### 7.1 Check Lambda Invocation

```bash
# View Lambda logs
LAMBDA_FUNCTION_NAME=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
  --output text)

aws logs tail /aws/lambda/$LAMBDA_FUNCTION_NAME --follow
```

### 7.2 Check Glue Job Status

```bash
# Get Glue job name
GLUE_JOB_NAME=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`GlueJobName`].OutputValue' \
  --output text)

# List recent job runs
aws glue get-job-runs --job-name $GLUE_JOB_NAME --max-results 5
```

### 7.3 View Glue Job Logs

```bash
# Get the latest job run ID
JOB_RUN_ID=$(aws glue get-job-runs \
  --job-name $GLUE_JOB_NAME \
  --max-results 1 \
  --query 'JobRuns[0].Id' \
  --output text)

# View logs in CloudWatch
aws logs tail /aws-glue/jobs/output --follow
```

## Step 8: Verify Processed Data

### 8.1 Check Processed Data in S3

```bash
PROCESSED_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`ProcessedDataBucketName`].OutputValue' \
  --output text)

# List processed data
aws s3 ls s3://$PROCESSED_BUCKET/processed/transactions/ --recursive
```

### 8.2 Verify Glue Data Catalog

```bash
GLUE_DB_NAME=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`GlueDatabaseName`].OutputValue' \
  --output text)

# Get table details
aws glue get-table \
  --database-name $GLUE_DB_NAME \
  --name transactions
```

## Step 9: Test Athena Queries

### 9.1 Run Sample Query

```bash
ATHENA_WORKGROUP=$(aws cloudformation describe-stacks \
  --stack-name ecommerce-analytics-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`AthenaWorkgroupName`].OutputValue' \
  --output text)

# Run a test query
aws athena start-query-execution \
  --work-group $ATHENA_WORKGROUP \
  --query-string "SELECT COUNT(*) as total_transactions FROM transactions LIMIT 1" \
  --result-configuration "OutputLocation=s3://$PROCESSED_BUCKET/athena-results/"
```

### 9.2 Query via AWS Console

1. Open AWS Athena console
2. Select workgroup: `ecommerce-analytics-workgroup`
3. Select database: `ecommerce_analytics_db`
4. Run queries from `athena/sample-queries.sql`

## Step 10: Set Up QuickSight Dashboard

Follow the instructions in `quicksight/dashboard-setup.md` to:
1. Connect QuickSight to Athena
2. Create visualizations
3. Build the dashboard

## Troubleshooting

### Issue: CloudFormation Stack Fails

**Check stack events:**
```bash
aws cloudformation describe-stack-events \
  --stack-name ecommerce-analytics-pipeline \
  --max-items 20
```

**Common issues:**
- Bucket names must be globally unique
- IAM permissions may need adjustment
- Region-specific service availability

### Issue: Lambda Not Triggering

**Check S3 event notification:**
```bash
aws s3api get-bucket-notification-configuration \
  --bucket $RAW_BUCKET
```

**Verify Lambda permissions:**
```bash
aws lambda get-policy --function-name $LAMBDA_FUNCTION_NAME
```

### Issue: Glue Job Fails

**Common causes:**
- Missing or incorrect S3 paths
- Schema mismatch in data
- Insufficient IAM permissions
- Data format issues

**Check job logs:**
```bash
aws logs tail /aws-glue/jobs/output --follow
```

### Issue: Athena Queries Return No Data

**Verify:**
1. Glue job completed successfully
2. Data exists in processed S3 bucket
3. Glue table schema is correct
4. Partition columns are properly set

**Repair partitions if needed:**
```sql
MSCK REPAIR TABLE transactions;
```

## Cost Optimization Tips

1. **Use appropriate Glue worker types**: G.1X is cost-effective for most workloads
2. **Enable job bookmarks**: Prevents reprocessing data
3. **Use Athena result caching**: Reduces query costs
4. **Set S3 lifecycle policies**: Archive old data to Glacier
5. **Monitor CloudWatch metrics**: Track usage and costs

## Cleanup

To remove all resources:

```bash
# Delete CloudFormation stack (this removes most resources)
aws cloudformation delete-stack --stack-name ecommerce-analytics-pipeline

# Wait for deletion
aws cloudformation wait stack-delete-complete \
  --stack-name ecommerce-analytics-pipeline

# Manually delete S3 buckets (if they contain data)
aws s3 rb s3://$RAW_BUCKET --force
aws s3 rb s3://$PROCESSED_BUCKET --force
aws s3 rb s3://$GLUE_SCRIPTS_BUCKET --force
```

## Next Steps

1. **Production Hardening**
   - Add error handling and retry logic
   - Implement data validation
   - Set up CloudWatch alarms
   - Enable encryption at rest

2. **Monitoring**
   - Set up CloudWatch dashboards
   - Create SNS alerts for job failures
   - Monitor costs with AWS Cost Explorer

3. **Security**
   - Enable S3 bucket encryption
   - Use KMS for key management
   - Implement least-privilege IAM policies
   - Enable VPC endpoints for private access

4. **Scaling**
   - Adjust Glue worker count based on data volume
   - Implement data archival strategy
   - Consider data lake architecture for larger scale

## Support

For issues or questions:
1. Check AWS CloudWatch Logs
2. Review CloudFormation stack events
3. Consult AWS documentation
4. Check AWS service health dashboard

