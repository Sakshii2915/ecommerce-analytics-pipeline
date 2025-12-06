# Deploy Without Access Keys - Alternative Methods

## Method 1: AWS CloudShell (Easiest - No Access Keys Needed!)

AWS CloudShell is a browser-based terminal that automatically uses your AWS Console session credentials. **No access keys required!**

### Steps:

1. **Open AWS Console**
   - Go to https://console.aws.amazon.com
   - Sign in to your AWS account

2. **Open CloudShell**
   - Click the CloudShell icon (terminal icon) in the top navigation bar
   - Wait for CloudShell to initialize (first time takes ~30 seconds)

3. **Clone Your Repository**
   ```bash
   cd ~
   git clone https://github.com/Sakshii2915/ecommerce-analytics-pipeline.git
   cd ecommerce-analytics-pipeline
   ```

4. **Run Deployment Script**
   ```bash
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

   Or if it's a Windows-based CloudShell:
   ```bash
   bash scripts/deploy.sh
   ```

5. **CloudShell automatically uses your console credentials!**
   - No `aws configure` needed
   - No access keys required
   - Uses your current AWS Console session

### Benefits:
- ✅ No access keys needed
- ✅ Secure (uses your console session)
- ✅ Pre-installed AWS CLI
- ✅ Free to use
- ✅ Works from any browser

---

## Method 2: AWS Console Manual Deployment

Deploy everything through the AWS Console web interface - no CLI needed!

### Step 1: Create S3 Buckets

1. Go to **S3 Console**: https://console.aws.amazon.com/s3
2. Click **"Create bucket"**
3. Create these buckets:
   - **Raw Data Bucket**: `ecommerce-raw-data-[your-account-id]`
   - **Processed Data Bucket**: `ecommerce-processed-data-[your-account-id]`
   - **Glue Scripts Bucket**: `ecommerce-glue-scripts-[your-account-id]`
4. For each bucket:
   - Uncheck "Block all public access"
   - Click "Create bucket"

### Step 2: Upload Glue Script

1. Go to your **Glue Scripts Bucket**
2. Create folder: `glue/`
3. Upload `glue/etl-job.py` to `glue/etl-job.py`

### Step 3: Deploy CloudFormation Stack

1. Go to **CloudFormation Console**: https://console.aws.amazon.com/cloudformation
2. Click **"Create stack"** → **"With new resources (standard)"**
3. **Template source**: Choose "Upload a template file"
4. Upload: `infrastructure/cloudformation-template.yaml`
5. Click **"Next"**
6. **Stack name**: `ecommerce-analytics-pipeline`
7. **Parameters**:
   - ProjectName: `ecommerce-analytics`
   - RawDataBucketName: `ecommerce-raw-data-[your-account-id]`
   - ProcessedDataBucketName: `ecommerce-processed-data-[your-account-id]`
8. Click **"Next"** → **"Next"** → **"Create stack"**
9. Wait for stack creation (5-10 minutes)

### Step 4: Update Lambda Function

1. Go to **Lambda Console**: https://console.aws.amazon.com/lambda
2. Find function: `ecommerce-analytics-TriggerGlueJob`
3. Upload `lambda/trigger-glue-job.py` as the function code
4. Update environment variables:
   - `PROCESSED_BUCKET`: Your processed data bucket name

### Step 5: Test the Pipeline

1. Generate sample data (locally):
   ```bash
   python data-generator/generate-sample-data.py
   ```

2. Upload to S3 (via Console):
   - Go to Raw Data Bucket
   - Create folder: `raw/`
   - Upload `transactions.csv` to `raw/transactions_20240101.csv`

3. Check Glue job execution in **Glue Console**

---

## Method 3: Local Demo Version (No AWS Needed!)

I can create a local version that simulates the pipeline using:
- Local file system instead of S3
- Python scripts instead of Glue
- SQLite instead of Athena
- Local dashboard instead of QuickSight

This lets you test the pipeline logic without any AWS setup!

---

## Method 4: AWS SAM/Serverless Framework (Alternative)

If you have AWS account access but prefer GUI:
- Use AWS SAM CLI (can work with console credentials)
- Use Serverless Framework (can use AWS profiles)

---

## Recommended: Use CloudShell (Method 1)

**CloudShell is the easiest option** - it combines:
- No access keys needed ✅
- Full CLI functionality ✅
- Secure (uses your session) ✅
- Pre-configured environment ✅

Just open CloudShell from AWS Console and run the deployment script!

---

## Quick CloudShell Commands

```bash
# 1. Clone repo
git clone https://github.com/Sakshii2915/ecommerce-analytics-pipeline.git
cd ecommerce-analytics-pipeline

# 2. Deploy
bash scripts/deploy.sh

# 3. Generate and upload test data
python3 data-generator/generate-sample-data.py
aws s3 cp data-generator/output/transactions.csv \
  s3://[your-raw-bucket]/raw/transactions_$(date +%Y%m%d).csv
```

That's it! CloudShell handles all the authentication automatically.

