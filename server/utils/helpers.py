"""
Helper functions and utilities
"""
from datetime import datetime
import random
import string

def generate_coupon_id() -> str:
    """Generate a unique coupon ID"""
    timestamp = int(datetime.now().timestamp())
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"COUPON-{timestamp}-{random_suffix}"

def generate_purchase_id() -> str:
    """Generate a unique purchase ID"""
    timestamp = int(datetime.now().timestamp())
    random_suffix = random.randint(1000, 9999)
    return f"PURCHASE-{timestamp}-{random_suffix}"

def generate_synthetic_adid(base_adid: str, index: int) -> str:
    """Generate synthetic ADID for demo purposes"""
    return f"{base_adid}-SYN{index}"

