"""
Setup script to generate data and run ETL before starting the dashboard on Render
"""

import os
import subprocess
import sys

def main():
    print("=" * 60)
    print("Render Setup - Generating Data and Running ETL")
    print("=" * 60)
    
    # Check if data already exists
    if os.path.exists("data/analytics.db"):
        print("✅ Database already exists, skipping data generation")
        return
    
    # Generate sample data
    print("Step 1: Generating sample transaction data...")
    try:
        subprocess.run([sys.executable, "generate_data.py"], check=True)
        print("✅ Data generation complete")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generating data: {e}")
        sys.exit(1)
    
    # Run ETL process
    print("Step 2: Running ETL process...")
    try:
        subprocess.run([sys.executable, "etl_process.py"], check=True)
        print("✅ ETL process complete")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in ETL process: {e}")
        sys.exit(1)
    
    print("=" * 60)
    print("Setup complete! Dashboard is ready to start.")
    print("=" * 60)

if __name__ == "__main__":
    main()


