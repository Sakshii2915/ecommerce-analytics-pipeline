"""
Generate sample e-commerce transaction data for local testing
"""

import csv
import random
from datetime import datetime, timedelta
import os

NUM_TRANSACTIONS = 100000
OUTPUT_DIR = "data/raw"
OUTPUT_FILE = "transactions.csv"

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
]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Apple Pay"]
REGIONS = ["North", "South", "East", "West", "Central"]
STORES = [f"STORE_{i:03d}" for i in range(1, 11)]

def generate_transaction_id():
    return f"TXN{random.randint(1000000, 9999999)}"

def generate_customer_id():
    return f"CUST{random.randint(10000, 99999)}"

def generate_transaction_date():
    days_ago = random.randint(0, 365)
    transaction_date = datetime.now() - timedelta(days=days_ago)
    transaction_date = transaction_date.replace(
        hour=random.randint(0, 23),
        minute=random.randint(0, 59),
        second=random.randint(0, 59)
    )
    return transaction_date.strftime('%Y-%m-%d %H:%M:%S')

def main():
    print("Generating sample transaction data...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    transactions = []
    transaction_ids = set()
    
    for i in range(NUM_TRANSACTIONS):
        txn_id = generate_transaction_id()
        while txn_id in transaction_ids:
            txn_id = generate_transaction_id()
        transaction_ids.add(txn_id)
        
        product_id, product_name, category, base_price = random.choice(PRODUCTS)
        quantity = random.choices([1, 2, 3, 4, 5], weights=[50, 30, 12, 5, 3])[0]
        price = round(base_price * random.uniform(0.9, 1.1), 2)
        total_amount = round(price * quantity, 2)
        
        transaction = {
            'transaction_id': txn_id,
            'customer_id': generate_customer_id(),
            'product_id': product_id,
            'product_name': product_name,
            'category': category,
            'price': price,
            'quantity': quantity,
            'total_amount': total_amount,
            'transaction_date': generate_transaction_date(),
            'payment_method': random.choice(PAYMENT_METHODS),
            'region': random.choice(REGIONS),
            'store_id': random.choice(STORES)
        }
        transactions.append(transaction)
        
        if (i + 1) % 10000 == 0:
            print(f"Generated {i + 1:,} transactions...")
    
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    fieldnames = list(transactions[0].keys())
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
    
    print(f"\n✅ Generated {len(transactions):,} transactions")
    print(f"📁 Saved to: {output_path}")
    print(f"💰 Total revenue: ${sum(t['total_amount'] for t in transactions):,.2f}")

if __name__ == "__main__":
    main()

