"""
Lambda function to automatically trigger Glue ETL job when new files are uploaded to S3

This function is triggered by S3 events and starts the Glue ETL job
to process the newly uploaded transaction data.
"""

import json
import boto3
import os
from datetime import datetime

glue_client = boto3.client('glue')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Lambda handler function triggered by S3 object creation events
    
    Args:
        event: S3 event containing bucket and object key information
        context: Lambda context object
    
    Returns:
        dict: Response with status code and message
    """
    
    # Get Glue job name from environment variable
    glue_job_name = os.environ.get('GLUE_JOB_NAME')
    processed_bucket = os.environ.get('PROCESSED_BUCKET', '')
    
    if not glue_job_name:
        raise ValueError("GLUE_JOB_NAME environment variable is not set")
    
    print(f"Received S3 event. Glue job name: {glue_job_name}")
    
    # Process each S3 event record
    job_run_ids = []
    
    for record in event.get('Records', []):
        # Extract S3 bucket and key
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        print(f"Processing file: s3://{bucket_name}/{object_key}")
        
        # Only process files in the 'raw/' prefix
        if not object_key.startswith('raw/'):
            print(f"Skipping file {object_key} - not in raw/ prefix")
            continue
        
        # Skip if file is too small (likely incomplete upload)
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            file_size = response.get('ContentLength', 0)
            
            if file_size < 100:  # Less than 100 bytes, likely incomplete
                print(f"Skipping file {object_key} - file too small ({file_size} bytes)")
                continue
        except Exception as e:
            print(f"Error checking file size: {str(e)}")
            continue
        
        # Prepare job arguments
        job_arguments = {
            '--raw_bucket': bucket_name,
            '--raw_key': object_key,
            '--processed_bucket': processed_bucket,
            '--enable-metrics': 'true',
            '--enable-continuous-cloudwatch-log': 'true'
        }
        
        try:
            # Start Glue job run
            response = glue_client.start_job_run(
                JobName=glue_job_name,
                Arguments=job_arguments
            )
            
            job_run_id = response['JobRunId']
            job_run_ids.append(job_run_id)
            
            print(f"Successfully started Glue job run: {job_run_id}")
            print(f"Job arguments: {json.dumps(job_arguments, indent=2)}")
            
        except Exception as e:
            error_message = f"Error starting Glue job: {str(e)}"
            print(error_message)
            # Don't fail the entire batch if one job fails
            continue
    
    if not job_run_ids:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'No Glue jobs were started (files may have been filtered out)',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Successfully triggered {len(job_run_ids)} Glue job run(s)',
            'job_run_ids': job_run_ids,
            'timestamp': datetime.utcnow().isoformat()
        })
    }

