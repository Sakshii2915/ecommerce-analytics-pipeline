"""
Sample Data Generator for E-Commerce Transaction Data

Generates realistic e-commerce transaction data for testing the analytics pipeline.
Creates CSV files with various transaction patterns, categories, and time distributions.
"""

import csv
import random
from datetime import datetime, timedelta
import os

# Configuration
NUM_TRANSACTIONS = 100000  # Number of transactions to generate
OUTPUT_DIR = "output"
OUTPUT_FILE = "transactions.csv"

# Sample data pools
PRODUCTS = [
    ("P001", "Wireless Headphones", "Electronics", 79.99),
    ("P002", "Laptop Stand", "Electronics", 29.99),
    ("P003", "USB-C Cable", "Electronics", 12.99),
    ("P004", "Coffee Maker", "Home & Kitchen", 89.99),
    ("P005", "Yoga Mat", "Sports & Outdoors", 24.99),
    ("P006", "Running Shoes", "Sports & Outdoors", 129.99),
    ("P007", "Bluetooth Speaker", "Electronics", 49.99),
    ("P008", "Desk Lamp", "Home & Kitchen", 34.99),
    ("P009", "Backpack", "Fashion", 59.99),
    ("P010", "Smart Watch", "Electronics", 199.99),
    ("P011", "Water Bottle", "Sports & Outdoors", 19.99),
    ("P012", "Phone Case", "Electronics", 14.99),
    ("P013", "Tablet", "Electronics", 299.99),
    ("P014", "Dumbbells Set", "Sports & Outdoors", 79.99),
    ("P015", "Kitchen Knife Set", "Home & Kitchen", 69.99),
    ("P016", "Sunglasses", "Fashion", 39.99),
    ("P017", "Gaming Mouse", "Electronics", 44.99),
    ("P018", "Throw Pillow", "Home & Kitchen", 19.99),
    ("P019", "T-Shirt", "Fashion", 24.99),
    ("P020", "Fitness Tracker", "Sports & Outdoors", 89.99),
]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Apple Pay", "Google Pay", "Bank Transfer"]
REGIONS = ["North", "South", "East", "West", "Central"]
STORES = [f"STORE_{i:03d}" for i in range(1, 21)]

def generate_transaction_id():
    """Generate a unique transaction ID"""
    return f"TXN{random.randint(1000000, 9999999)}"

def generate_customer_id():
    """Generate a customer ID"""
    return f"CUST{random.randint(10000, 99999)}"

def generate_transaction_date(start_date=None, end_date=None):
    """Generate a random transaction date within the specified range"""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=365)
    if end_date is None:
        end_date = datetime.now()
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    random_date = start_date + timedelta(days=random_days)
    
    # Add random time within the day
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    random_seconds = random.randint(0, 59)
    
    return random_date.replace(hour=random_hours, minute=random_minutes, second=random_seconds)

def generate_transactions(num_transactions):
    """Generate a list of transaction records"""
    transactions = []
    transaction_ids = set()
    
    for i in range(num_transactions):
        # Ensure unique transaction IDs
        txn_id = generate_transaction_id()
        while txn_id in transaction_ids:
            txn_id = generate_transaction_id()
        transaction_ids.add(txn_id)
        
        # Select random product
        product_id, product_name, category, base_price = random.choice(PRODUCTS)
        
        # Generate quantity (1-5 items, weighted towards 1-2)
        quantity = random.choices(
            [1, 2, 3, 4, 5],
            weights=[50, 30, 12, 5, 3]
        )[0]
        
        # Add some price variation (±10%)
        price_variation = random.uniform(0.9, 1.1)
        price = round(base_price * price_variation, 2)
        
        # Calculate total amount
        total_amount = round(price * quantity, 2)
        
        # Generate transaction date (last 365 days, with more recent transactions)
        # Weight towards recent dates
        days_ago = random.choices(
            range(365),
            weights=[365 - d for d in range(365)]
        )[0]
        transaction_date = datetime.now() - timedelta(days=days_ago)
        transaction_date = transaction_date.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        # Create transaction record
        transaction = {
            'transaction_id': txn_id,
            'customer_id': generate_customer_id(),
            'product_id': product_id,
            'product_name': product_name,
            'category': category,
            'price': price,
            'quantity': quantity,
            'total_amount': total_amount,
            'transaction_date': transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': random.choice(PAYMENT_METHODS),
            'region': random.choice(REGIONS),
            'store_id': random.choice(STORES)
        }
        
        transactions.append(transaction)
        
        if (i + 1) % 10000 == 0:
            print(f"Generated {i + 1:,} transactions...")
    
    return transactions

def write_csv(transactions, filepath):
    """Write transactions to CSV file"""
    if not transactions:
        print("No transactions to write")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)
    
    # Get field names from first transaction
    fieldnames = list(transactions[0].keys())
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"Successfully wrote {len(transactions):,} transactions to {filepath}")

def main():
    """Main function to generate and save sample data"""
    print("=" * 60)
    print("E-Commerce Transaction Data Generator")
    print("=" * 60)
    print(f"Generating {NUM_TRANSACTIONS:,} transactions...")
    print()
    
    # Generate transactions
    transactions = generate_transactions(NUM_TRANSACTIONS)
    
    # Write to CSV
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    write_csv(transactions, output_path)
    
    # Print statistics
    print()
    print("=" * 60)
    print("Generation Statistics")
    print("=" * 60)
    print(f"Total transactions: {len(transactions):,}")
    print(f"Total revenue: ${sum(t['total_amount'] for t in transactions):,.2f}")
    print(f"Average transaction value: ${sum(t['total_amount'] for t in transactions) / len(transactions):,.2f}")
    
    # Category breakdown
    category_counts = {}
    for t in transactions:
        category_counts[t['category']] = category_counts.get(t['category'], 0) + 1
    
    print("\nTransactions by category:")
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {category}: {count:,} ({count/len(transactions)*100:.1f}%)")
    
    # Payment method breakdown
    payment_counts = {}
    for t in transactions:
        payment_counts[t['payment_method']] = payment_counts.get(t['payment_method'], 0) + 1
    
    print("\nTransactions by payment method:")
    for method, count in sorted(payment_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {method}: {count:,} ({count/len(transactions)*100:.1f}%)")
    
    print()
    print(f"Data file saved to: {output_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()

