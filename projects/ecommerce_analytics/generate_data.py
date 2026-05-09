import csv
import sqlite3
import random
from datetime import datetime, timedelta
import os

# Set seed for reproducibility
random.seed(42)

# --- CONFIGURATION ---
NUM_CUSTOMERS = 200
NUM_PRODUCTS = 50
NUM_ORDERS = 1000
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# --- DATA POOLS ---
first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy", "Mallory", "Niaj", "Olivia", "Peggy", "Sybil", "Trent", "Victor", "Walter", "Pooja", "Aarav", "Rahul", "Sneha", "Karan"]
last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Yadav", "Sharma", "Singh", "Patel", "Kumar"]
countries = ["United States", "United Kingdom", "Canada", "Australia", "India", "Germany", "France", "Japan"]
segments = ["Consumer", "Corporate", "Home Office"]
categories = {
    "Technology": ["Phones", "Accessories", "Machines", "Copiers"],
    "Furniture": ["Bookcases", "Chairs", "Labels", "Tables", "Furnishings"],
    "Office Supplies": ["Storage", "Art", "Binders", "Appliances", "Paper", "Envelopes"]
}
ship_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]

def random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

def generate_customers():
    customers = []
    for i in range(1, NUM_CUSTOMERS + 1):
        customers.append({
            "CustomerID": i,
            "FirstName": random.choice(first_names),
            "LastName": random.choice(last_names),
            "Country": random.choice(countries),
            "Segment": random.choice(segments)
        })
    return customers

def generate_products():
    products = []
    for i in range(1, NUM_PRODUCTS + 1):
        cat = random.choice(list(categories.keys()))
        subcat = random.choice(categories[cat])
        cost = round(random.uniform(10.0, 500.0), 2)
        price = round(cost * random.uniform(1.2, 2.5), 2) # 20% to 150% markup
        products.append({
            "ProductID": i,
            "ProductName": f"{subcat} {random.randint(1000, 9999)}",
            "Category": cat,
            "SubCategory": subcat,
            "Price": price,
            "Cost": cost
        })
    return products

def generate_orders_and_items(customers, products):
    orders = []
    order_items = []
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2023, 12, 31)
    
    item_id = 1
    for i in range(1, NUM_ORDERS + 1):
        customer = random.choice(customers)
        order_date = random_date(start_date, end_date)
        shipping_delay = random.randint(1, 7)
        shipping_date = order_date + timedelta(days=shipping_delay)
        
        orders.append({
            "OrderID": i,
            "CustomerID": customer["CustomerID"],
            "OrderDate": order_date.strftime("%Y-%m-%d"),
            "ShippingDate": shipping_date.strftime("%Y-%m-%d"),
            "ShipMode": random.choice(ship_modes)
        })
        
        # 1 to 5 items per order
        num_items = random.randint(1, 5)
        order_products = random.sample(products, num_items)
        for prod in order_products:
            quantity = random.randint(1, 10)
            discount = random.choice([0.0, 0.0, 0.0, 0.05, 0.1, 0.15, 0.2]) # higher chance of 0 discount
            order_items.append({
                "OrderItemID": item_id,
                "OrderID": i,
                "ProductID": prod["ProductID"],
                "Quantity": quantity,
                "Discount": discount
            })
            item_id += 1
            
    return orders, order_items

def save_to_csv(data, filename, fieldnames):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved {filename}")

def save_to_sqlite(customers, products, orders, order_items):
    db_path = os.path.join(OUTPUT_DIR, 'ecommerce.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create Tables
    cursor.execute("""
    CREATE TABLE Customers (
        CustomerID INTEGER PRIMARY KEY,
        FirstName TEXT,
        LastName TEXT,
        Country TEXT,
        Segment TEXT
    )""")
    
    cursor.execute("""
    CREATE TABLE Products (
        ProductID INTEGER PRIMARY KEY,
        ProductName TEXT,
        Category TEXT,
        SubCategory TEXT,
        Price REAL,
        Cost REAL
    )""")
    
    cursor.execute("""
    CREATE TABLE Orders (
        OrderID INTEGER PRIMARY KEY,
        CustomerID INTEGER,
        OrderDate TEXT,
        ShippingDate TEXT,
        ShipMode TEXT,
        FOREIGN KEY(CustomerID) REFERENCES Customers(CustomerID)
    )""")
    
    cursor.execute("""
    CREATE TABLE Order_Items (
        OrderItemID INTEGER PRIMARY KEY,
        OrderID INTEGER,
        ProductID INTEGER,
        Quantity INTEGER,
        Discount REAL,
        FOREIGN KEY(OrderID) REFERENCES Orders(OrderID),
        FOREIGN KEY(ProductID) REFERENCES Products(ProductID)
    )""")
    
    # Insert Data
    cursor.executemany("INSERT INTO Customers VALUES (:CustomerID, :FirstName, :LastName, :Country, :Segment)", customers)
    cursor.executemany("INSERT INTO Products VALUES (:ProductID, :ProductName, :Category, :SubCategory, :Price, :Cost)", products)
    cursor.executemany("INSERT INTO Orders VALUES (:OrderID, :CustomerID, :OrderDate, :ShippingDate, :ShipMode)", orders)
    cursor.executemany("INSERT INTO Order_Items VALUES (:OrderItemID, :OrderID, :ProductID, :Quantity, :Discount)", order_items)
    
    conn.commit()
    conn.close()
    print(f"Saved all data to SQLite database: {db_path}")

def main():
    print("Generating synthetic e-commerce data...")
    customers = generate_customers()
    products = generate_products()
    orders, order_items = generate_orders_and_items(customers, products)
    
    # Save to CSV
    save_to_csv(customers, 'customers.csv', ["CustomerID", "FirstName", "LastName", "Country", "Segment"])
    save_to_csv(products, 'products.csv', ["ProductID", "ProductName", "Category", "SubCategory", "Price", "Cost"])
    save_to_csv(orders, 'orders.csv', ["OrderID", "CustomerID", "OrderDate", "ShippingDate", "ShipMode"])
    save_to_csv(order_items, 'order_items.csv', ["OrderItemID", "OrderID", "ProductID", "Quantity", "Discount"])
    
    # Save to SQLite
    save_to_sqlite(customers, products, orders, order_items)
    print("Data generation complete!")

if __name__ == "__main__":
    main()
