# AWS Setup Guide for E-Commerce Analytics Pipeline

## Step 1: Create AWS Account (if you don't have one)

1. Go to https://aws.amazon.com
2. Click "Create an AWS Account"
3. Follow the signup process
4. You'll need a credit card (AWS Free Tier includes 12 months free for many services)

## Step 2: Access AWS Console

1. Go to https://console.aws.amazon.com
2. Sign in with your root account email

## Step 3: Create IAM User and Access Keys

### Option A: Using Root Account (if you have access)

1. **Go to IAM Console**
   - In AWS Console, search for "IAM" in the top search bar
   - Click on "IAM" service

2. **Create a New User**
   - Click "Users" in the left sidebar
   - Click "Create user"
   - Enter username: `ecommerce-analytics-user`
   - Click "Next"

3. **Set Permissions**
   - Select "Attach policies directly"
   - Search and select these policies:
     - `AdministratorAccess` (for full deployment) OR
     - Custom policies with these permissions:
       - `AmazonS3FullAccess`
       - `AWSGlueServiceRole`
       - `AWSLambda_FullAccess`
       - `AmazonAthenaFullAccess`
       - `AmazonQuickSightFullAccess`
       - `CloudFormationFullAccess`
       - `IAMFullAccess`
   - Click "Next" → "Create user"

4. **Create Access Keys**
   - Click on the user you just created
   - Go to "Security credentials" tab
   - Scroll to "Access keys" section
   - Click "Create access key"
   - Select "Command Line Interface (CLI)"
   - Click "Next" → "Create access key"
   - **IMPORTANT**: Copy both:
     - Access Key ID
     - Secret Access Key (shown only once!)

### Option B: If IAM is Not Accessible

If you cannot access IAM, you may need to:

1. **Check your account type**
   - Some AWS accounts (like AWS Educate) have restrictions
   - Contact your AWS administrator

2. **Use AWS CloudShell** (alternative)
   - Go to AWS Console
   - Click the CloudShell icon (top right)
   - This provides temporary credentials

3. **Contact AWS Support**
   - If you're the account owner but can't access IAM
   - There may be account-level restrictions

## Step 4: Configure AWS CLI

Once you have your Access Key ID and Secret Access Key:

```powershell
aws configure
```

Enter when prompted:
- **AWS Access Key ID**: [paste your Access Key ID]
- **AWS Secret Access Key**: [paste your Secret Access Key]
- **Default region name**: `us-east-1` (or your preferred region)
- **Default output format**: `json` (just press Enter)

## Step 5: Verify Configuration

```powershell
aws sts get-caller-identity
```

This should return your account ID and user ARN.

## Step 6: Deploy the Pipeline

Once credentials are configured, run:

```powershell
.\scripts\deploy.ps1
```

## Troubleshooting

### "Unable to locate credentials"
- Make sure you ran `aws configure`
- Check credentials are saved: `aws configure list`

### "Access Denied" errors
- Your IAM user needs the permissions listed above
- Check IAM policies are attached correctly

### "IAM not accessible"
- Try signing in as root account
- Check if you're using AWS Educate or similar restricted account
- Some organizations restrict IAM access

### Alternative: Manual Deployment

If you can't use automated deployment, see `DEPLOYMENT.md` for manual step-by-step instructions.

## Cost Considerations

**AWS Free Tier includes:**
- 5 GB S3 storage (first 12 months)
- 750 hours/month of Lambda (always free)
- 1 million Glue requests/month (first 2 months)
- 10 GB Athena queries/month (first 2 months)

**Estimated costs for this project:**
- Small scale (< 1M transactions): ~$5-20/month
- Medium scale (1-10M transactions): ~$25-50/month
- Large scale (> 10M transactions): ~$100+/month

## Need Help?

- AWS Documentation: https://docs.aws.amazon.com
- AWS Support: https://console.aws.amazon.com/support
- AWS Free Tier: https://aws.amazon.com/free

