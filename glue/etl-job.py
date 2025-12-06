"""
AWS Glue ETL Job for E-Commerce Transaction Data Processing

This script performs:
1. Schema normalization
2. Duplicate removal
3. Data type conversion
4. Date-based partitioning
5. Parquet format conversion for optimized querying
"""

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F
from pyspark.sql.types import *
from datetime import datetime
import boto3

# Initialize Glue context
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'raw_bucket',
    'raw_key',
    'processed_bucket'
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Get parameters
raw_bucket = args['raw_bucket']
raw_key = args['raw_key']
processed_bucket = args['processed_bucket']

# S3 paths
raw_data_path = f"s3://{raw_bucket}/{raw_key}"
processed_data_path = f"s3://{processed_bucket}/processed/transactions/"

print(f"Reading raw data from: {raw_data_path}")
print(f"Writing processed data to: {processed_data_path}")

# Read raw data
# Support both CSV and JSON formats
if raw_key.endswith('.csv'):
    # Read CSV with schema inference
    raw_df = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_data_path)
elif raw_key.endswith('.json'):
    raw_df = spark.read.json(raw_data_path)
else:
    raise ValueError(f"Unsupported file format: {raw_key}")

print(f"Raw data count: {raw_df.count()}")
print(f"Raw data schema:")
raw_df.printSchema()

# Define expected schema for normalization
expected_schema = StructType([
    StructField("transaction_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("total_amount", DoubleType(), True),
    StructField("transaction_date", TimestampType(), True),
    StructField("payment_method", StringType(), True),
    StructField("region", StringType(), True),
    StructField("store_id", StringType(), True)
])

# Normalize column names (handle various formats)
column_mapping = {
    'transaction_id': ['transaction_id', 'transactionid', 'id', 'txn_id'],
    'customer_id': ['customer_id', 'customerid', 'customer'],
    'product_id': ['product_id', 'productid', 'product'],
    'product_name': ['product_name', 'productname', 'name', 'item'],
    'category': ['category', 'cat', 'product_category'],
    'price': ['price', 'unit_price', 'unitprice'],
    'quantity': ['quantity', 'qty', 'qty_sold'],
    'total_amount': ['total_amount', 'total', 'amount', 'totalamount', 'revenue'],
    'transaction_date': ['transaction_date', 'date', 'timestamp', 'transactiondate', 'txn_date'],
    'payment_method': ['payment_method', 'payment', 'paymentmethod', 'payment_type'],
    'region': ['region', 'location', 'geo'],
    'store_id': ['store_id', 'storeid', 'store']
}

# Function to normalize column names
def normalize_columns(df):
    """Normalize column names to match expected schema"""
    for standard_name, variations in column_mapping.items():
        for col in df.columns:
            if col.lower() in [v.lower() for v in variations]:
                if col != standard_name:
                    df = df.withColumnRenamed(col, standard_name)
                break
    return df

# Normalize columns
normalized_df = normalize_columns(raw_df)

# Add missing columns with null values
for field in expected_schema.fields:
    if field.name not in normalized_df.columns:
        normalized_df = normalized_df.withColumn(field.name, F.lit(None).cast(field.dataType))

# Select only expected columns
normalized_df = normalized_df.select([field.name for field in expected_schema.fields])

# Data type conversions and cleaning
cleaned_df = normalized_df \
    .withColumn("transaction_id", F.trim(F.col("transaction_id"))) \
    .withColumn("customer_id", F.trim(F.col("customer_id"))) \
    .withColumn("product_name", F.trim(F.col("product_name"))) \
    .withColumn("category", F.trim(F.col("category"))) \
    .withColumn("payment_method", F.trim(F.col("payment_method"))) \
    .withColumn("region", F.trim(F.col("region"))) \
    .withColumn("store_id", F.trim(F.col("store_id")))

# Convert transaction_date to timestamp if it's a string
if "transaction_date" in cleaned_df.columns:
    cleaned_df = cleaned_df.withColumn(
        "transaction_date",
        F.coalesce(
            F.to_timestamp(F.col("transaction_date"), "yyyy-MM-dd HH:mm:ss"),
            F.to_timestamp(F.col("transaction_date"), "yyyy-MM-dd"),
            F.to_timestamp(F.col("transaction_date"), "MM/dd/yyyy HH:mm:ss"),
            F.to_timestamp(F.col("transaction_date"), "MM/dd/yyyy"),
            F.col("transaction_date")
        )
    )

# Ensure numeric fields are properly typed
for col_name in ["price", "quantity", "total_amount"]:
    if col_name in cleaned_df.columns:
        cleaned_df = cleaned_df.withColumn(
            col_name,
            F.coalesce(F.col(col_name).cast("double"), F.lit(0.0))
        )

# Calculate total_amount if missing or incorrect
cleaned_df = cleaned_df.withColumn(
    "total_amount",
    F.when(
        (F.col("total_amount").isNull()) | (F.col("total_amount") == 0),
        F.col("price") * F.col("quantity")
    ).otherwise(F.col("total_amount"))
)

# Remove duplicates based on transaction_id
print("Removing duplicates...")
initial_count = cleaned_df.count()
cleaned_df = cleaned_df.dropDuplicates(["transaction_id"])
final_count = cleaned_df.count()
duplicates_removed = initial_count - final_count
print(f"Removed {duplicates_removed} duplicate records")

# Remove rows with null transaction_id or transaction_date
cleaned_df = cleaned_df.filter(
    F.col("transaction_id").isNotNull() & 
    F.col("transaction_date").isNotNull()
)

# Add partition columns (year, month, day) for efficient querying
cleaned_df = cleaned_df \
    .withColumn("year", F.year(F.col("transaction_date"))) \
    .withColumn("month", F.month(F.col("transaction_date"))) \
    .withColumn("day", F.dayofmonth(F.col("transaction_date"))) \
    .withColumn("hour", F.hour(F.col("transaction_date")))

# Add additional derived columns for analytics
cleaned_df = cleaned_df \
    .withColumn("day_of_week", F.dayofweek(F.col("transaction_date"))) \
    .withColumn("week_of_year", F.weekofyear(F.col("transaction_date"))) \
    .withColumn("quarter", F.quarter(F.col("transaction_date")))

print(f"Final cleaned data count: {cleaned_df.count()}")
print("Final schema:")
cleaned_df.printSchema()

# Convert to DynamicFrame for Glue
dynamic_frame = DynamicFrame.fromDF(cleaned_df, glueContext, "cleaned_transactions")

# Write to S3 in Parquet format with partitioning
print(f"Writing processed data to: {processed_data_path}")

# Use Glue's write_dynamic_frame for better integration
glueContext.write_dynamic_frame.from_options(
    frame=dynamic_frame,
    connection_type="s3",
    connection_options={
        "path": processed_data_path,
        "partitionKeys": ["year", "month", "day"]
    },
    format="parquet",
    format_options={
        "compression": "snappy"  # Use Snappy compression for better performance
    }
)

print("ETL job completed successfully!")

# Update Glue Data Catalog
print("Updating Glue Data Catalog...")
try:
    # Create or update table in Glue Data Catalog
    glue_client = boto3.client('glue')
    database_name = 'ecommerce_analytics_db'
    table_name = 'transactions'
    
    # Get the schema from the DataFrame
    schema = []
    for field in cleaned_df.schema.fields:
        schema.append({
            'Name': field.name,
            'Type': str(field.dataType).replace('Type()', '').lower()
        })
    
    table_input = {
        'Name': table_name,
        'StorageDescriptor': {
            'Columns': schema,
            'Location': processed_data_path,
            'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
            'SerdeInfo': {
                'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
            },
            'Parameters': {
                'classification': 'parquet',
                'compressionType': 'snappy'
            }
        },
        'PartitionKeys': [
            {'Name': 'year', 'Type': 'int'},
            {'Name': 'month', 'Type': 'int'},
            {'Name': 'day', 'Type': 'int'}
        ],
        'TableType': 'EXTERNAL_TABLE'
    }
    
    try:
        # Try to update existing table
        glue_client.update_table(
            DatabaseName=database_name,
            TableInput=table_input
        )
        print(f"Updated table {table_name} in Glue Data Catalog")
    except glue_client.exceptions.EntityNotFoundException:
        # Create new table if it doesn't exist
        glue_client.create_table(
            DatabaseName=database_name,
            TableInput=table_input
        )
        print(f"Created table {table_name} in Glue Data Catalog")
        
except Exception as e:
    print(f"Warning: Could not update Glue Data Catalog: {str(e)}")
    print("You may need to manually create/update the table in Glue Data Catalog")

job.commit()

