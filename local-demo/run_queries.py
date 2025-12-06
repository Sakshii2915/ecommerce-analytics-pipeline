"""
Run analytics queries on the processed data (like Athena queries)
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "data/analytics.db"

def run_query(query, description):
    """Execute a SQL query and display results"""
    print(f"\n{'='*60}")
    print(f"Query: {description}")
    print('='*60)
    
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print(df.to_string(index=False))
    print(f"\nRows returned: {len(df)}")
    return df

def main():
    print("=" * 60)
    print("E-Commerce Analytics Queries")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: {DB_PATH} not found!")
        print("   Run 'python etl_process.py' first")
        return
    
    # Query 1: Total Revenue
    run_query("""
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(DISTINCT customer_id) as unique_customers,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_transaction_value
        FROM transactions
    """, "Overall Business KPIs")
    
    # Query 2: Revenue by Category
    run_query("""
        SELECT 
            category,
            COUNT(*) as transaction_count,
            SUM(total_amount) as category_revenue,
            AVG(total_amount) as avg_transaction_value
        FROM transactions
        GROUP BY category
        ORDER BY category_revenue DESC
    """, "Revenue by Category")
    
    # Query 3: Top Products
    run_query("""
        SELECT 
            product_name,
            category,
            SUM(total_amount) as total_revenue,
            SUM(quantity) as total_quantity_sold,
            COUNT(*) as transaction_count
        FROM transactions
        GROUP BY product_name, category
        ORDER BY total_revenue DESC
        LIMIT 10
    """, "Top 10 Products by Revenue")
    
    # Query 4: Peak Hours
    run_query("""
        SELECT 
            hour,
            COUNT(*) as transaction_count,
            SUM(total_amount) as hourly_revenue
        FROM transactions
        GROUP BY hour
        ORDER BY transaction_count DESC
    """, "Peak Transaction Hours")
    
    # Query 5: Payment Methods
    run_query("""
        SELECT 
            payment_method,
            COUNT(*) as transaction_count,
            SUM(total_amount) as total_revenue,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions), 2) as percentage
        FROM transactions
        GROUP BY payment_method
        ORDER BY total_revenue DESC
    """, "Payment Method Analysis")
    
    # Query 6: Revenue by Region
    run_query("""
        SELECT 
            region,
            COUNT(*) as transaction_count,
            SUM(total_amount) as regional_revenue,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM transactions
        GROUP BY region
        ORDER BY regional_revenue DESC
    """, "Revenue by Region")
    
    print("\n" + "=" * 60)
    print("All queries completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

