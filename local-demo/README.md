# Local E-Commerce Analytics Pipeline Demo

This is a **local version** of the analytics pipeline that runs entirely on your machine - **no AWS account needed!**

## What This Does

Simulates the full AWS pipeline using local tools:
- **Local files** instead of S3
- **Python/Pandas** instead of AWS Glue
- **SQLite** instead of Athena
- **Local web dashboard** instead of QuickSight

## Requirements

- Python 3.8+
- pip

## Installation

```bash
cd local-demo
pip install -r requirements.txt
```

## Quick Start

### 1. Generate Sample Data

```bash
python generate_data.py
```

This creates `data/raw/transactions.csv` with 100,000 transactions.

### 2. Run ETL Process

```bash
python etl_process.py
```

This will:
- Read raw CSV data
- Clean and normalize
- Remove duplicates
- Partition by date
- Save as Parquet files in `data/processed/`
- Create SQLite database

### 3. Run Analytics Queries

```bash
python run_queries.py
```

This executes sample queries and shows results.

### 4. View Dashboard (Optional)

```bash
python dashboard.py
```

Opens a local web dashboard at http://localhost:8050

## Project Structure

```
local-demo/
├── generate_data.py      # Generate sample transaction data
├── etl_process.py        # ETL processing (like Glue job)
├── run_queries.py        # Run analytics queries (like Athena)
├── dashboard.py          # Local dashboard (like QuickSight)
├── data/
│   ├── raw/              # Raw CSV files
│   ├── processed/        # Processed Parquet files
│   └── analytics.db      # SQLite database
└── requirements.txt      # Python dependencies
```

## Features

✅ **Same ETL Logic**: Uses the same transformation logic as AWS Glue  
✅ **Parquet Format**: Same optimized storage format  
✅ **Partitioning**: Date-based partitioning like AWS  
✅ **SQL Queries**: SQLite supports similar SQL to Athena  
✅ **Visualizations**: Local dashboard with charts  

## Performance

- Processes 100K transactions in ~10-30 seconds
- Parquet files are ~70% smaller than CSV
- Queries run in milliseconds

## Use Cases

- **Testing**: Test ETL logic before AWS deployment
- **Learning**: Understand pipeline concepts locally
- **Development**: Develop and debug transformations
- **Demo**: Show pipeline functionality without AWS

## Next Steps

Once you're ready for AWS:
1. Follow `DEPLOY_WITHOUT_ACCESS_KEYS.md`
2. Use CloudShell for easy deployment
3. Your local code can be adapted for AWS Glue

