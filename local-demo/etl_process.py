"""
Local ETL process that mimics AWS Glue functionality
Processes raw CSV data and converts to optimized Parquet format
"""

import pandas as pd
import os
from datetime import datetime
import pyarrow.parquet as pq
import pyarrow as pa

RAW_DATA_PATH = "data/raw/transactions.csv"
PROCESSED_DIR = "data/processed"
DB_PATH = "data/analytics.db"

def normalize_schema(df):
    """Normalize column names"""
    column_mapping = {
        'transaction_id': ['transaction_id', 'transactionid', 'id', 'txn_id'],
        'customer_id': ['customer_id', 'customerid', 'customer'],
        'product_id': ['product_id', 'productid', 'product'],
        'product_name': ['product_name', 'productname', 'name', 'item'],
        'category': ['category', 'cat', 'product_category'],
        'price': ['price', 'unit_price', 'unitprice'],
        'quantity': ['quantity', 'qty', 'qty_sold'],
        'total_amount': ['total', 'amount', 'totalamount', 'revenue'],
        'transaction_date': ['transaction_date', 'date', 'timestamp', 'transactiondate'],
        'payment_method': ['payment_method', 'payment', 'paymentmethod'],
        'region': ['region', 'location', 'geo'],
        'store_id': ['store_id', 'storeid', 'store']
    }
    
    for standard_name, variations in column_mapping.items():
        for col in df.columns:
            if col.lower() in [v.lower() for v in variations]:
                if col != standard_name:
                    df = df.rename(columns={col: standard_name})
                break
    
    return df

def clean_data(df):
    """Clean and transform data"""
    print("Cleaning data...")
    
    # Trim string columns
    string_cols = ['transaction_id', 'customer_id', 'product_name', 'category', 
                   'payment_method', 'region', 'store_id']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Convert transaction_date to datetime
    if 'transaction_date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    
    # Ensure numeric types
    numeric_cols = ['price', 'quantity', 'total_amount']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Calculate total_amount if missing
    if 'total_amount' in df.columns and 'price' in df.columns and 'quantity' in df.columns:
        mask = (df['total_amount'].isna()) | (df['total_amount'] == 0)
        df.loc[mask, 'total_amount'] = df.loc[mask, 'price'] * df.loc[mask, 'quantity']
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates(subset=['transaction_id'], keep='first')
    duplicates_removed = initial_count - len(df)
    print(f"  Removed {duplicates_removed} duplicate records")
    
    # Remove rows with null transaction_id or transaction_date
    df = df[df['transaction_id'].notna() & df['transaction_date'].notna()]
    
    return df

def add_partitions(df):
    """Add partition columns"""
    if 'transaction_date' in df.columns:
        df['year'] = df['transaction_date'].dt.year
        df['month'] = df['transaction_date'].dt.month
        df['day'] = df['transaction_date'].dt.day
        df['hour'] = df['transaction_date'].dt.hour
        df['day_of_week'] = df['transaction_date'].dt.dayofweek + 1
        df['week_of_year'] = df['transaction_date'].dt.isocalendar().week
        df['quarter'] = df['transaction_date'].dt.quarter
    
    return df

def save_to_parquet(df):
    """Save data as Parquet files partitioned by date"""
    print("Saving to Parquet format...")
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Group by year/month/day and save separate files
    grouped = df.groupby(['year', 'month', 'day'])
    
    file_count = 0
    for (year, month, day), group_df in grouped:
        partition_path = os.path.join(PROCESSED_DIR, f"year={year}/month={month}/day={day}")
        os.makedirs(partition_path, exist_ok=True)
        
        file_path = os.path.join(partition_path, "data.parquet")
        group_df.to_parquet(file_path, engine='pyarrow', compression='snappy', index=False)
        file_count += 1
    
    print(f"  Saved {file_count} partitioned Parquet files")
    return file_count

def create_sqlite_db(df):
    """Create SQLite database for querying"""
    print("Creating SQLite database...")
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    
    # Save to SQLite
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    
    # Create indexes for better query performance
    conn.execute("CREATE INDEX IF NOT EXISTS idx_date ON transactions(transaction_date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_category ON transactions(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_customer ON transactions(customer_id)")
    
    conn.close()
    print(f"  Database created: {DB_PATH}")

def main():
    print("=" * 60)
    print("Local ETL Process - E-Commerce Analytics Pipeline")
    print("=" * 60)
    print()
    
    # Read raw data
    print(f"Reading raw data from: {RAW_DATA_PATH}")
    if not os.path.exists(RAW_DATA_PATH):
        print(f"❌ Error: {RAW_DATA_PATH} not found!")
        print("   Run 'python generate_data.py' first")
        return
    
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"  Loaded {len(df):,} records")
    
    # Normalize schema
    print("Normalizing schema...")
    df = normalize_schema(df)
    
    # Clean data
    df = clean_data(df)
    print(f"  Final record count: {len(df):,}")
    
    # Add partitions
    df = add_partitions(df)
    
    # Save to Parquet
    file_count = save_to_parquet(df)
    
    # Create SQLite database
    create_sqlite_db(df)
    
    # Statistics
    print()
    print("=" * 60)
    print("ETL Process Complete!")
    print("=" * 60)
    print(f"✅ Processed {len(df):,} transactions")
    print(f"✅ Created {file_count} partitioned Parquet files")
    print(f"✅ Created SQLite database: {DB_PATH}")
    print(f"💰 Total revenue: ${df['total_amount'].sum():,.2f}")
    print()
    print("Next steps:")
    print("  1. Run queries: python run_queries.py")
    print("  2. View dashboard: python dashboard.py")

if __name__ == "__main__":
    main()

