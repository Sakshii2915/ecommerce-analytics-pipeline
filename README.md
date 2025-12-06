# Serverless E-Commerce Analytics Pipeline

A fully serverless analytics pipeline that processes raw e-commerce transaction data from S3, transforms it using AWS Glue, and makes it query-ready for large-scale analysis in Athena. The pipeline automatically triggers on new data uploads, performs schema normalization, removes duplicates, partitions data by date, and writes optimized Parquet files for efficient querying.

## Architecture Overview

```
S3 (Raw Data) → Lambda Trigger → AWS Glue ETL → S3 (Processed Parquet) → Athena → QuickSight
```

### Key Components

1. **S3 Buckets**
   - Raw data bucket: Stores incoming transaction data (CSV/JSON)
   - Processed data bucket: Stores optimized Parquet files partitioned by date

2. **AWS Glue**
   - ETL job that performs:
     - Schema normalization
     - Duplicate removal
     - Data type conversion
     - Date-based partitioning
     - Parquet format conversion

3. **AWS Lambda**
   - Automatically triggers Glue job when new files are uploaded to raw S3 bucket

4. **AWS Athena**
   - Query engine for analyzing processed data
   - Uses Glue Data Catalog for schema management

5. **Amazon QuickSight**
   - Interactive dashboards for visualization
   - Revenue trends, top categories, peak hours, KPIs

## Performance Benefits

- **~80% faster** analytical queries compared to unoptimized raw data
- **Cost reduction** through columnar Parquet format and partitioning
- **Automatic scaling** with serverless architecture
- **Zero infrastructure management**

## Project Structure

```
ecommerce-analytics-pipeline/
├── infrastructure/
│   └── cloudformation-template.yaml    # AWS infrastructure as code
├── glue/
│   └── etl-job.py                      # Glue ETL script
├── lambda/
│   └── trigger-glue-job.py             # Lambda function to trigger Glue
├── athena/
│   └── sample-queries.sql              # Example Athena queries
├── quicksight/
│   └── dashboard-setup.md              # QuickSight configuration guide
├── data-generator/
│   └── generate-sample-data.py         # Script to generate test data
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.8+
- boto3 library

## Deployment Steps

### 1. Deploy Infrastructure

```bash
aws cloudformation create-stack \
  --stack-name ecommerce-analytics-pipeline \
  --template-body file://infrastructure/cloudformation-template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters ParameterKey=ProjectName,ParameterValue=ecommerce-analytics
```

### 2. Upload Sample Data

```bash
python data-generator/generate-sample-data.py
aws s3 cp data-generator/output/transactions.csv \
  s3://<raw-bucket-name>/raw/transactions_$(date +%Y%m%d).csv
```

### 3. Verify Glue Job Execution

Check AWS Glue console to see the job running automatically after data upload.

### 4. Query Data in Athena

Run queries from `athena/sample-queries.sql` in Athena console.

### 5. Create QuickSight Dashboard

Follow instructions in `quicksight/dashboard-setup.md` to create visualizations.

## Configuration

Update the following parameters in `cloudformation-template.yaml`:
- `ProjectName`: Your project identifier
- `RawDataBucketName`: Name for raw data S3 bucket
- `ProcessedDataBucketName`: Name for processed data S3 bucket

## Cost Optimization

- Parquet format reduces storage by ~70%
- Partitioning enables partition pruning, scanning only relevant data
- Serverless architecture means you only pay for what you use
- Athena charges per TB scanned (reduced by partitioning)

## Monitoring

- CloudWatch Logs for Glue job execution
- CloudWatch Metrics for Lambda invocations
- Athena query history in AWS Console

## Cleanup

To remove all resources:

```bash
aws cloudformation delete-stack --stack-name ecommerce-analytics-pipeline
```

## License

MIT License

