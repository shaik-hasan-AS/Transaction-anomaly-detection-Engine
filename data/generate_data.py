import random
import uuid
import os
import math
from datetime import datetime, timedelta
import psycopg2
from faker import Faker
import numpy as np

fake = Faker()

DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "fraud_db"),
    "user": os.environ.get("DB_USER", "fraud_user"),
    "password": os.environ.get("DB_PASSWORD", "fraud_password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5433")
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

# Real-world cities with lat/lon to create realistic hubs
CITIES = [
    {"name": "New York", "country": "USA", "lat": 40.7128, "lon": -74.0060},
    {"name": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278},
    {"name": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503},
    {"name": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093},
    {"name": "Toronto", "country": "Canada", "lat": 43.6510, "lon": -79.3470},
]

# Merchant categories with realistic price distributions (mean, std_dev for lognormal)
CATEGORIES = {
    "Coffee Shop": {"mu": 1.5, "sigma": 0.5}, # ~$5
    "Fast Food": {"mu": 2.5, "sigma": 0.5}, # ~$15
    "Groceries": {"mu": 4.0, "sigma": 0.6}, # ~$60
    "Gas Station": {"mu": 3.7, "sigma": 0.4}, # ~$40
    "Electronics": {"mu": 5.8, "sigma": 0.8}, # ~$350
    "Travel": {"mu": 6.2, "sigma": 0.7}, # ~$500
    "Online Retail": {"mu": 3.9, "sigma": 1.0}, # ~$50 to $200
}

CURRENCIES = {
    "USA": "USD",
    "UK": "GBP",
    "Japan": "JPY",
    "Australia": "AUD",
    "Canada": "CAD"
}

PROFILES = [
    {
        "name": "Budget",
        "weight": 0.5, 
        "amount_multiplier": 0.5,
        "decline_chance": 0.1, 
        "categories": ["Fast Food", "Coffee Shop", "Groceries"],
        "travel_chance": 0.01
    },
    {
        "name": "Average",
        "weight": 0.35,
        "amount_multiplier": 1.0,
        "decline_chance": 0.03,
        "categories": ["Fast Food", "Coffee Shop", "Groceries", "Gas Station", "Online Retail"],
        "travel_chance": 0.05
    },
    {
        "name": "Business",
        "weight": 0.1,
        "amount_multiplier": 2.5,
        "decline_chance": 0.01,
        "categories": ["Travel", "Gas Station", "Coffee Shop", "Electronics"],
        "travel_chance": 0.3
    },
    {
        "name": "High-Net-Worth",
        "weight": 0.05,
        "amount_multiplier": 5.0,
        "decline_chance": 0.005,
        "categories": ["Travel", "Electronics", "Online Retail", "Groceries"],
        "travel_chance": 0.2
    }
]

def generate_customers(n=500):
    customers = []
    profile_names = [p["name"] for p in PROFILES]
    profile_weights = [p["weight"] for p in PROFILES]
    
    for _ in range(n):
        city = random.choice(CITIES)
        profile = random.choices(profile_names, weights=profile_weights)[0]
        customers.append({
            "customer_id": str(uuid.uuid4()),
            "name": fake.name(),
            "country": city["country"],
            "home_lat": city["lat"] + random.uniform(-0.1, 0.1), # slight jitter around city center
            "home_lon": city["lon"] + random.uniform(-0.1, 0.1),
            "created_at": datetime.now() - timedelta(days=random.randint(100, 1000)),
            "profile": profile
        })
    return customers

def generate_accounts(customers, n_per_customer=(1, 2)):
    accounts = []
    for c in customers:
        num_accounts = random.randint(*n_per_customer)
        for _ in range(num_accounts):
            accounts.append({
                "account_id": str(uuid.uuid4()),
                "customer_id": c["customer_id"],
                "account_type": random.choice(["Checking", "Savings", "Credit"]),
                "created_at": c["created_at"] + timedelta(days=random.randint(1, 30)),
                "status": "ACTIVE"
            })
    return accounts

def generate_cards(accounts, n_per_account=(1, 2)):
    cards = []
    for a in accounts:
        num_cards = random.randint(*n_per_account)
        for _ in range(num_cards):
            cards.append({
                "card_id": str(uuid.uuid4()),
                "account_id": a["account_id"],
                "card_type": random.choice(["Visa", "MasterCard", "Amex"]),
                "created_at": a["created_at"] + timedelta(days=random.randint(1, 10)),
                "status": "ACTIVE"
            })
    return cards

def generate_merchants(n=1000):
    merchants = []
    for _ in range(n):
        city = random.choice(CITIES)
        category = random.choice(list(CATEGORIES.keys()))
        merchants.append({
            "merchant_id": str(uuid.uuid4()),
            "merchant_name": fake.company(),
            "category": category,
            "latitude": city["lat"] + random.uniform(-0.2, 0.2),
            "longitude": city["lon"] + random.uniform(-0.2, 0.2),
            "country": city["country"]
        })
    return merchants

def generate_devices(n=200):
    devices = []
    types = ["Mobile", "Desktop", "Tablet"]
    oses = ["iOS", "Android", "Windows", "MacOS"]
    for _ in range(n):
        devices.append({
            "device_id": str(uuid.uuid4()),
            "device_type": random.choice(types),
            "operating_system": random.choice(oses),
            "created_at": datetime.now() - timedelta(days=random.randint(10, 500))
        })
    return devices

def generate_transactions(customers, accounts, cards, merchants, devices, start_date, num_days=30, tx_per_day=1500):
    transactions = []
    
    # Pre-map accounts to customers to find home location
    account_to_customer = {a["account_id"]: next(c for c in customers if c["customer_id"] == a["customer_id"]) for a in accounts}
    card_to_account = {c["card_id"]: c["account_id"] for c in cards}
    
    # Assign 1-2 devices per account to avoid endless "New Device" flags
    account_devices = {a["account_id"]: random.sample(devices, random.randint(1, 2)) for a in accounts}

    # Generate random timestamps weighted towards daytime (8am - 8pm)
    timestamps = []
    for _ in range(num_days * tx_per_day):
        hour = int(np.random.normal(14, 4))
        hour = max(6, min(23, hour)) # Force 6 AM to 11 PM to avoid accidental Late Night anomalies
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        day_offset = random.randint(0, num_days - 1)
        
        tx_time = start_date + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)
        
        if tx_time.weekday() >= 5:
            if random.random() < 0.2:
                tx_time = tx_time.replace(hour=max(6, min(23, tx_time.hour + 4)))
                
        timestamps.append(tx_time)
        
    timestamps.sort()
    
    for tx_time in timestamps:
        card = random.choice(cards)
        account_id = card_to_account[card["card_id"]]
        customer = account_to_customer[account_id]
        profile_data = next(p for p in PROFILES if p["name"] == customer["profile"])
        
        # Base transactions are ALWAYS domestic to prevent accidental Impossible Travel or Foreign TX
        local_merchants = [m for m in merchants if m["country"] == customer["country"]]
        if not local_merchants:
            local_merchants = merchants
            
        favored_merchants = [m for m in local_merchants if m["category"] in profile_data["categories"]]
        
        if favored_merchants and random.random() < 0.7:
            merchant = random.choice(favored_merchants)
        else:
            merchant = random.choice(local_merchants)
            
        device = random.choice(account_devices[account_id])
        
        # Realistic pricing based on log-normal distribution for the category and profile modifier
        cat_params = CATEGORIES[merchant["category"]]
        base_amount = np.random.lognormal(cat_params["mu"], cat_params["sigma"])
        amount = round(base_amount * profile_data["amount_multiplier"], 2)
        amount = max(1.0, amount) # Ensure at least $1
        
        # Determine Status and Currency
        status = "DECLINED" if random.random() < profile_data["decline_chance"] else "SUCCESS"
        currency = CURRENCIES.get(merchant["country"], "USD")
        
        transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": account_id,
            "card_id": card["card_id"],
            "merchant_id": merchant["merchant_id"],
            "device_id": device["device_id"],
            "timestamp": tx_time,
            "amount": amount,
            "currency": currency,
            "latitude": merchant["latitude"],
            "longitude": merchant["longitude"],
            "country": merchant["country"],
            "ip_address": fake.ipv4(),
            "payment_method": "Card",
            "status": status
        })
        
    return transactions

def inject_anomalies(transactions, customers, accounts, cards, merchants, devices):
    # We will inject 50 of each type of anomaly to ensure a perfect mix
    
    # 1. High Velocity Attack (Card Testing)
    for _ in range(50):
        target_card = random.choice(cards)
        base_time = datetime.now() - timedelta(days=random.randint(1, 10))
        for i in range(15): # 15 tx in 75 seconds
            transactions.append({
                "transaction_id": str(uuid.uuid4()),
                "account_id": target_card["account_id"],
                "card_id": target_card["card_id"],
                "merchant_id": random.choice(merchants)["merchant_id"],
                "device_id": random.choice(devices)["device_id"],
                "timestamp": base_time + timedelta(seconds=i*5),
                "amount": round(random.uniform(1.0, 3.0), 2),
                "currency": "USD",
                "latitude": 0.0,
                "longitude": 0.0,
                "country": "Unknown",
                "ip_address": fake.ipv4(),
                "payment_method": "Card",
                "status": "SUCCESS"
            })

    # 2. Value Anomaly
    for _ in range(50):
        target_card2 = random.choice(cards)
        merchant2 = random.choice(merchants)
        transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": target_card2["account_id"],
            "card_id": target_card2["card_id"],
            "merchant_id": merchant2["merchant_id"],
            "device_id": random.choice(devices)["device_id"],
            "timestamp": datetime.now() - timedelta(days=random.randint(1, 5)),
            "amount": 125000.00, # Extremely high amount
            "currency": "USD",
            "latitude": merchant2["latitude"],
            "longitude": merchant2["longitude"],
            "country": merchant2["country"],
            "ip_address": fake.ipv4(),
            "payment_method": "Card",
            "status": "SUCCESS"
        })

    # 3. Impossible Travel
    for _ in range(50):
        target_card3 = random.choice(cards)
        device3 = random.choice(devices)
        time3 = datetime.now() - timedelta(days=random.randint(1, 5))
        
        # Tx 1: New York
        ny_merchant = next((m for m in merchants if m["country"] == "USA"), merchants[0])
        transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": target_card3["account_id"],
            "card_id": target_card3["card_id"],
            "merchant_id": ny_merchant["merchant_id"],
            "device_id": device3["device_id"],
            "timestamp": time3,
            "amount": 50.0,
            "currency": "USD",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "country": "USA",
            "ip_address": fake.ipv4(),
            "payment_method": "Card",
            "status": "SUCCESS"
        })
        
        # Tx 2: Tokyo 10 mins later
        tokyo_merchant = next((m for m in merchants if m["country"] == "Japan"), merchants[1])
        transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": target_card3["account_id"],
            "card_id": target_card3["card_id"],
            "merchant_id": tokyo_merchant["merchant_id"],
            "device_id": device3["device_id"],
            "timestamp": time3 + timedelta(minutes=10),
            "amount": 120.0,
            "currency": "JPY",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "country": "Japan",
            "ip_address": fake.ipv4(),
            "payment_method": "Card",
            "status": "SUCCESS"
        })

    # 4. Micro-Charge Testing
    for _ in range(50):
        target_card4 = random.choice(cards)
        base_time4 = datetime.now() - timedelta(days=random.randint(1, 10))
        for i in range(4): # 4 micro-charges in 2 hours
            transactions.append({
                "transaction_id": str(uuid.uuid4()),
                "account_id": target_card4["account_id"],
                "card_id": target_card4["card_id"],
                "merchant_id": random.choice(merchants)["merchant_id"],
                "device_id": random.choice(devices)["device_id"],
                "timestamp": base_time4 + timedelta(minutes=i*30),
                "amount": round(random.uniform(0.5, 1.5), 2),
                "currency": "USD",
                "latitude": 0.0,
                "longitude": 0.0,
                "country": "Unknown",
                "ip_address": fake.ipv4(),
                "payment_method": "Card",
                "status": "SUCCESS"
            })

    # 5. Late Night Transaction
    for _ in range(50):
        target_card5 = random.choice(cards)
        merchant5 = random.choice(merchants)
        base_time5 = datetime.now() - timedelta(days=random.randint(1, 10))
        base_time5 = base_time5.replace(hour=random.randint(2, 4), minute=random.randint(0, 59)) # 2 AM to 4 AM
        transactions.append({
            "transaction_id": str(uuid.uuid4()),
            "account_id": target_card5["account_id"],
            "card_id": target_card5["card_id"],
            "merchant_id": merchant5["merchant_id"],
            "device_id": random.choice(devices)["device_id"],
            "timestamp": base_time5,
            "amount": round(random.uniform(50.0, 300.0), 2),
            "currency": CURRENCIES.get(merchant5["country"], "USD"),
            "latitude": merchant5["latitude"],
            "longitude": merchant5["longitude"],
            "country": merchant5["country"],
            "ip_address": fake.ipv4(),
            "payment_method": "Card",
            "status": "SUCCESS"
        })

    # 6. Cross-Border Transaction
    for _ in range(50):
        target_card6 = random.choice(cards)
        account_id = target_card6["account_id"]
        customer_id = next(a["customer_id"] for a in accounts if a["account_id"] == account_id)
        customer_country = next(c["country"] for c in customers if c["customer_id"] == customer_id)
        
        foreign_merchants = [m for m in merchants if m["country"] != customer_country]
        if foreign_merchants:
            merchant6 = random.choice(foreign_merchants)
            transactions.append({
                "transaction_id": str(uuid.uuid4()),
                "account_id": target_card6["account_id"],
                "card_id": target_card6["card_id"],
                "merchant_id": merchant6["merchant_id"],
                "device_id": random.choice(devices)["device_id"],
                "timestamp": datetime.now() - timedelta(days=random.randint(1, 10)),
                "amount": round(random.uniform(100.0, 500.0), 2),
                "currency": CURRENCIES.get(merchant6["country"], "USD"),
                "latitude": merchant6["latitude"],
                "longitude": merchant6["longitude"],
                "country": merchant6["country"],
                "ip_address": fake.ipv4(),
                "payment_method": "Card",
                "status": "SUCCESS"
            })

    return transactions

def main():
    print("Connecting to DB...")
    conn = get_db_connection()
    cur = conn.cursor()

    print("Generating highly realistic data...")
    customers = generate_customers(500)
    accounts = generate_accounts(customers)
    cards = generate_cards(accounts)
    merchants = generate_merchants(1000)
    devices = generate_devices(300)
    
    start_date = datetime.now() - timedelta(days=30)
    transactions = generate_transactions(customers, accounts, cards, merchants, devices, start_date)
    transactions = inject_anomalies(transactions, customers, accounts, cards, merchants, devices)

    print("Clearing old data...")
    cur.execute("TRUNCATE TABLE transactions, devices, merchants, cards, accounts, customers CASCADE;")
    
    print("Inserting data...")
    
    cur.executemany("INSERT INTO customers (customer_id, name, country, created_at) VALUES (%s, %s, %s, %s)", 
                    [(c["customer_id"], c["name"], c["country"], c["created_at"]) for c in customers])
    
    cur.executemany("INSERT INTO accounts (account_id, customer_id, account_type, created_at, status) VALUES (%s, %s, %s, %s, %s)", 
                    [(a["account_id"], a["customer_id"], a["account_type"], a["created_at"], a["status"]) for a in accounts])
    
    cur.executemany("INSERT INTO cards (card_id, account_id, card_type, created_at, status) VALUES (%s, %s, %s, %s, %s)", 
                    [(c["card_id"], c["account_id"], c["card_type"], c["created_at"], c["status"]) for c in cards])
    
    cur.executemany("INSERT INTO merchants (merchant_id, merchant_name, category, latitude, longitude, country) VALUES (%s, %s, %s, %s, %s, %s)", 
                    [(m["merchant_id"], m["merchant_name"], m["category"], m["latitude"], m["longitude"], m["country"]) for m in merchants])
    
    cur.executemany("INSERT INTO devices (device_id, device_type, operating_system, created_at) VALUES (%s, %s, %s, %s)", 
                    [(d["device_id"], d["device_type"], d["operating_system"], d["created_at"]) for d in devices])
    
    tx_tuples = [
        (t["transaction_id"], t["account_id"], t["card_id"], t["merchant_id"], t["device_id"], 
         t["timestamp"], t["amount"], t["currency"], t["latitude"], t["longitude"], 
         t["country"], t["ip_address"], t["payment_method"], t["status"])
        for t in transactions
    ]
    cur.executemany("""
        INSERT INTO transactions 
        (transaction_id, account_id, card_id, merchant_id, device_id, timestamp, amount, currency, latitude, longitude, country, ip_address, payment_method, status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, tx_tuples)

    conn.commit()
    cur.close()
    conn.close()
    print(f"Successfully generated and inserted {len(transactions)} realistic transactions.")

if __name__ == "__main__":
    main()
