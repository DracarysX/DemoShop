"""
FastAPI Coupon Server
Run with: uvicorn main:app --reload --port 8080
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
from collections import defaultdict
import random
import string

app = FastAPI(title="DemoShop Coupon API")

# Enable CORS for React Native
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CouponRequest(BaseModel):
    adid: str
    productName: str

class CouponResponse(BaseModel):
    couponId: str
    discount: float

class PurchaseItem(BaseModel):
    name: str
    price: float
    discount: float
    finalPrice: float

class PurchaseRequest(BaseModel):
    adid: str
    items: List[PurchaseItem]
    total: float
    trackerEnabled: bool = True  # Default to True for backwards compatibility

class PurchaseResponse(BaseModel):
    success: bool
    purchaseId: str
    timestamp: str

# In-memory storage for demo purposes
coupon_history = []
purchase_history = []

def generate_coupon_id() -> str:
    """Generate a unique coupon ID"""
    timestamp = int(datetime.now().timestamp())
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"COUPON-{timestamp}-{random_suffix}"

@app.get("/")
async def root():
    return {
        "message": "DemoShop Coupon API",
        "version": "1.0.0",
        "endpoints": {
            "POST /coupon": "Request a discount coupon"
        }
    }

@app.post("/coupon", response_model=CouponResponse)
async def create_coupon(request: CouponRequest):
    """
    Create a discount coupon for a product
    
    Args:
        request: Contains adid (advertising ID) and productName
        
    Returns:
        CouponResponse with couponId and discount amount
    """
    print(f"[Server] Received coupon request:")
    print(f"  - ADID: {request.adid}")
    print(f"  - Product: {request.productName}")
    
    # Generate coupon
    coupon_id = generate_coupon_id()
    discount = 0.2  # 20% discount
    
    # Store in history
    coupon_record = {
        "couponId": coupon_id,
        "adid": request.adid,
        "productName": request.productName,
        "discount": discount,
        "timestamp": datetime.now().isoformat()
    }
    coupon_history.append(coupon_record)
    
    response = CouponResponse(
        couponId=coupon_id,
        discount=discount
    )
    
    print(f"[Server] Sending coupon response:")
    print(f"  - Coupon ID: {coupon_id}")
    print(f"  - Discount: {discount * 100}%")
    
    return response

@app.get("/coupons")
async def get_coupon_history():
    """Get all issued coupons (for debugging)"""
    return {
        "total": len(coupon_history),
        "coupons": coupon_history
    }

def generate_synthetic_purchases(original_request: PurchaseRequest) -> List[Dict]:
    """
    DEMO/TESTING FUNCTION - Generate synthetic purchase data for analytics testing.
    Creates 2 additional fake purchases for each real purchase:
    1. Same purchase details with a different ADID
    2. Same items but without coupons (discount = 0)
    
    DELETE THIS FUNCTION when you want to use only real data.
    """
    synthetic_purchases = []
    
    # Generate a random ADID by modifying the original
    import hashlib
    random_suffix_1 = hashlib.md5(f"{original_request.adid}-synthetic-1".encode()).hexdigest()[:8]
    synthetic_adid_1 = f"{original_request.adid[:16]}-{random_suffix_1}"
    
    random_suffix_2 = hashlib.md5(f"{original_request.adid}-synthetic-2".encode()).hexdigest()[:8]
    synthetic_adid_2 = f"{original_request.adid[:16]}-{random_suffix_2}"
    
    # 1. Same purchase with different ADID
    synthetic_purchase_1 = {
        "adid": synthetic_adid_1,
        "items": [item.dict() for item in original_request.items],
        "total": original_request.total,
        "trackerEnabled": original_request.trackerEnabled
    }
    synthetic_purchases.append(synthetic_purchase_1)
    
    # 2. ONLY items that were bought WITHOUT coupons (don't include items that had discounts)
    items_without_coupons = []
    total_without_coupons = 0.0
    
    for item in original_request.items:
        # Only include items that originally had NO discount
        if item.discount == 0:
            items_without_coupons.append(item.dict())
            total_without_coupons += item.finalPrice
    
    # Only create this synthetic purchase if there were items without coupons
    if items_without_coupons:
        synthetic_purchase_2 = {
            "adid": synthetic_adid_2,
            "items": items_without_coupons,
            "total": total_without_coupons,
            "trackerEnabled": False  # Assume tracker is off for non-coupon users
        }
        synthetic_purchases.append(synthetic_purchase_2)
    
    return synthetic_purchases


@app.post("/purchase", response_model=PurchaseResponse)
async def record_purchase(request: PurchaseRequest):
    """
    Record a purchase
    
    Args:
        request: Contains adid, items purchased, and total amount
        
    Returns:
        PurchaseResponse with success status and purchase ID
    """
    print(f"[Server] Received purchase:")
    print(f"  - ADID: {request.adid}")
    print(f"  - Items: {len(request.items)}")
    print(f"  - Total: ${request.total:.2f}")
    print(f"  - Tracker: {'ON' if request.trackerEnabled else 'OFF'}")
    
    # Generate purchase ID
    timestamp = int(datetime.now().timestamp())
    purchase_id = f"PURCHASE-{timestamp}-{random.randint(1000, 9999)}"
    
    # Store purchase
    purchase_record = {
        "purchaseId": purchase_id,
        "adid": request.adid,
        "items": [item.dict() for item in request.items],
        "total": request.total,
        "trackerEnabled": request.trackerEnabled,
        "timestamp": datetime.now().isoformat()
    }
    purchase_history.append(purchase_record)
    
    print(f"[Server] Purchase recorded: {purchase_id}")
    
    # DEMO/TESTING: Generate synthetic purchases for analytics testing
    # DELETE THIS BLOCK when you want to use only real data
    synthetic_purchases = generate_synthetic_purchases(request)
    for idx, synthetic_purchase in enumerate(synthetic_purchases, 1):
        synthetic_timestamp = int(datetime.now().timestamp())
        synthetic_purchase_id = f"SYNTHETIC-{synthetic_timestamp}-{random.randint(1000, 9999)}"
        
        synthetic_record = {
            "purchaseId": synthetic_purchase_id,
            "adid": synthetic_purchase["adid"],
            "items": synthetic_purchase["items"],
            "total": synthetic_purchase["total"],
            "trackerEnabled": synthetic_purchase["trackerEnabled"],
            "timestamp": datetime.now().isoformat()
        }
        purchase_history.append(synthetic_record)
        print(f"[Server] Synthetic purchase {idx} recorded: {synthetic_purchase_id}")
    # END OF DEMO/TESTING BLOCK
    
    return PurchaseResponse(
        success=True,
        purchaseId=purchase_id,
        timestamp=purchase_record["timestamp"]
    )

@app.get("/analytics", response_class=HTMLResponse)
async def get_analytics():
    """
    Display analytics dashboard with revenue per ADID
    """
    # Calculate analytics per ADID - for ALL purchases
    analytics: Dict[str, Dict] = defaultdict(lambda: {
        "purchases": 0,
        "purchases_with_coupon": 0,
        "purchases_without_coupon": 0,
        "total_revenue": 0.0,
        "revenue_with_coupon": 0.0,
        "revenue_without_coupon": 0.0,
        "total_savings": 0.0,
        "items_purchased": 0,
        "tracker_enabled": False
    })
    
    # Calculate analytics per product
    product_analytics: Dict[str, Dict] = defaultdict(lambda: {
        "tracker_on_with_coupon": {"quantity": 0, "revenue": 0.0, "savings": 0.0},
        "tracker_on_without_coupon": {"quantity": 0, "revenue": 0.0, "savings": 0.0},
        "tracker_off": {"quantity": 0, "revenue": 0.0, "savings": 0.0}
    })
    
    # Track ADIDs with tracker on vs off
    adids_tracker_on = set()
    adids_tracker_off = set()
    
    for purchase in purchase_history:
        adid = purchase["adid"]
        tracker_enabled = purchase.get("trackerEnabled", True)
        
        # Track ADIDs by tracker status
        if tracker_enabled:
            adids_tracker_on.add(adid)
        else:
            adids_tracker_off.add(adid)
        
        # Separate items with and without coupons
        discounted_items = [item for item in purchase["items"] if item["discount"] > 0]
        non_discounted_items = [item for item in purchase["items"] if item["discount"] == 0]
        
        # Process ALL items (with or without coupons)
        has_coupon_items = len(discounted_items) > 0
        has_non_coupon_items = len(non_discounted_items) > 0
        
        analytics[adid]["purchases"] += 1
        analytics[adid]["tracker_enabled"] = tracker_enabled
        
        # Count purchases by type
        if has_coupon_items:
            analytics[adid]["purchases_with_coupon"] += 1
        if has_non_coupon_items:
            analytics[adid]["purchases_without_coupon"] += 1
        
        # Process items WITH coupons
        for item in discounted_items:
            analytics[adid]["total_revenue"] += item["finalPrice"]
            analytics[adid]["revenue_with_coupon"] += item["finalPrice"]
            analytics[adid]["items_purchased"] += 1
            
            original_price = item["price"]
            final_price = item["finalPrice"]
            savings = original_price - final_price
            analytics[adid]["total_savings"] += savings
            
            # Product-level analytics
            product_name = item["name"]
            if tracker_enabled:
                product_analytics[product_name]["tracker_on_with_coupon"]["quantity"] += 1
                product_analytics[product_name]["tracker_on_with_coupon"]["revenue"] += final_price
                product_analytics[product_name]["tracker_on_with_coupon"]["savings"] += savings
            else:
                product_analytics[product_name]["tracker_off"]["quantity"] += 1
                product_analytics[product_name]["tracker_off"]["revenue"] += final_price
                product_analytics[product_name]["tracker_off"]["savings"] += savings
        
        # Process items WITHOUT coupons
        for item in non_discounted_items:
            analytics[adid]["total_revenue"] += item["finalPrice"]
            analytics[adid]["revenue_without_coupon"] += item["finalPrice"]
            analytics[adid]["items_purchased"] += 1
            
            # Product-level analytics
            product_name = item["name"]
            if tracker_enabled:
                product_analytics[product_name]["tracker_on_without_coupon"]["quantity"] += 1
                product_analytics[product_name]["tracker_on_without_coupon"]["revenue"] += item["finalPrice"]
            else:
                product_analytics[product_name]["tracker_off"]["quantity"] += 1
                product_analytics[product_name]["tracker_off"]["revenue"] += item["finalPrice"]
    
    # Calculate totals by tracker status and coupon usage
    total_tracker_on = sum(a["total_revenue"] for a in analytics.values() if a["tracker_enabled"])
    total_tracker_off = sum(a["total_revenue"] for a in analytics.values() if not a["tracker_enabled"])
    
    revenue_with_coupon = sum(a["revenue_with_coupon"] for a in analytics.values())
    revenue_without_coupon = sum(a["revenue_without_coupon"] for a in analytics.values())
    
    purchases_with_coupon = sum(a["purchases_with_coupon"] for a in analytics.values())
    purchases_without_coupon = sum(a["purchases_without_coupon"] for a in analytics.values())
    
    purchases_tracker_on = sum(a["purchases"] for a in analytics.values() if a["tracker_enabled"])
    purchases_tracker_off = sum(a["purchases"] for a in analytics.values() if not a["tracker_enabled"])
    
    # Calculate percentage of ADIDs with tracker on
    total_unique_adids = len(adids_tracker_on | adids_tracker_off)
    tracker_on_percentage = (len(adids_tracker_on) / total_unique_adids * 100) if total_unique_adids > 0 else 0
    
    # Calculate revenue projection if 100% had tracker enabled
    # Average revenue per ADID with tracker on
    avg_revenue_tracker_on = total_tracker_on / len(adids_tracker_on) if len(adids_tracker_on) > 0 else 0
    
    # Current total revenue
    current_total_revenue = total_tracker_on + total_tracker_off
    
    # Projected revenue if all ADIDs had tracker enabled
    projected_revenue_100 = avg_revenue_tracker_on * total_unique_adids if total_unique_adids > 0 else 0
    
    # Additional revenue and percentage increase
    additional_revenue = projected_revenue_100 - current_total_revenue
    percentage_increase = (additional_revenue / current_total_revenue * 100) if current_total_revenue > 0 else 0
    
    # Generate HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DemoShop Analytics Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            
            .header h1 {
                font-size: 48px;
                font-weight: 700;
                margin-bottom: 10px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            .header p {
                font-size: 18px;
                opacity: 0.9;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .stat-card {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
            }
            
            .stat-value {
                font-size: 36px;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .stat-label {
                font-size: 14px;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            .table-container {
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            
            .table-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
            }
            
            .table-header h2 {
                font-size: 28px;
                font-weight: 600;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
            }
            
            thead {
                background: #f9fafb;
            }
            
            th {
                padding: 20px;
                text-align: left;
                font-weight: 600;
                color: #374151;
                text-transform: uppercase;
                font-size: 12px;
                letter-spacing: 0.5px;
                border-bottom: 2px solid #e5e7eb;
            }
            
            td {
                padding: 20px;
                border-bottom: 1px solid #e5e7eb;
                color: #1f2937;
            }
            
            tbody tr:hover {
                background: #f9fafb;
                transition: background 0.2s;
            }
            
            .adid-cell {
                font-family: 'Courier New', monospace;
                font-size: 13px;
                color: #667eea;
                font-weight: 600;
            }
            
            .revenue-cell {
                font-size: 18px;
                font-weight: 700;
                color: #10b981;
            }
            
            .savings-cell {
                font-size: 16px;
                color: #f59e0b;
                font-weight: 600;
            }
            
            .empty-state {
                padding: 60px;
                text-align: center;
                color: #9ca3af;
            }
            
            .empty-state-icon {
                font-size: 64px;
                margin-bottom: 20px;
            }
            
            .refresh-button {
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: white;
                color: #667eea;
                border: none;
                padding: 15px 30px;
                border-radius: 50px;
                font-weight: 600;
                font-size: 14px;
                cursor: pointer;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                transition: transform 0.2s;
            }
            
            .refresh-button:hover {
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 DemoShop Analytics</h1>
                <p>Real-time Revenue & Performance Dashboard</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">""" + str(len(analytics)) + """</div>
                    <div class="stat-label">Total Customers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">""" + str(sum(a["purchases"] for a in analytics.values())) + """</div>
                    <div class="stat-label">Total Purchases</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$""" + f"{current_total_revenue:.2f}" + """</div>
                    <div class="stat-label">Total Revenue</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$""" + f"{sum(a['total_savings'] for a in analytics.values()):.2f}" + """</div>
                    <div class="stat-label">Total Discounts Given</div>
                </div>
            </div>
            
            <div class="stats-grid" style="margin-top: 20px;">
                <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div class="stat-value">""" + str(purchases_with_coupon) + """</div>
                    <div class="stat-label">Purchases WITH Coupons</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                    <div class="stat-value">""" + str(purchases_without_coupon) + """</div>
                    <div class="stat-label">Purchases WITHOUT Coupons</div>
                </div>
                <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div class="stat-value">""" + f"{tracker_on_percentage:.1f}%" + """</div>
                    <div class="stat-label">ADIDs with Tracker ON</div>
                </div>
            </div>
            
            <div class="table-container" style="margin-top: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: 3px solid #ffd700;">
                <div class="table-header" style="background: rgba(255,255,255,0.1);">
                    <h2>💰 Revenue Projection: 100% Tracker Adoption</h2>
                </div>
                <div style="padding: 30px; color: white;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px;">
                        <div style="text-align: center;">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Current Revenue</div>
                            <div style="font-size: 32px; font-weight: 700;">$""" + f"{current_total_revenue:.2f}" + """</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Projected Revenue (100%)</div>
                            <div style="font-size: 32px; font-weight: 700; color: #ffd700;">$""" + f"{projected_revenue_100:.2f}" + """</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Additional Revenue</div>
                            <div style="font-size: 32px; font-weight: 700; color: #00ff88;">+$""" + f"{additional_revenue:.2f}" + """</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Increase</div>
                            <div style="font-size: 32px; font-weight: 700; color: #00ff88;">+""" + f"{percentage_increase:.1f}%" + """</div>
                        </div>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); padding: 15px; border-radius: 10px; text-align: center; font-size: 16px;">
                        <strong>📈 If all """ + str(total_unique_adids) + """ customers had tracker enabled, revenue would increase by $""" + f"{additional_revenue:.2f}" + """ (""" + f"{percentage_increase:.1f}%" + """)</strong>
                    </div>
                </div>
            </div>
            
            <div class="table-container">
                <div class="table-header">
                    <h2>Revenue by Advertising ID</h2>
                </div>
    """
    
    if analytics:
        html_content += """
                <table>
                    <thead>
                        <tr>
                            <th>Advertising ID</th>
                            <th>Tracker</th>
                            <th>Purchases</th>
                            <th>Items</th>
                            <th>Revenue (w/ Coupon)</th>
                            <th>Revenue (w/o Coupon)</th>
                            <th>Total Revenue</th>
                            <th>Savings</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Sort by revenue (highest first)
        sorted_analytics = sorted(analytics.items(), key=lambda x: x[1]["total_revenue"], reverse=True)
        
        for adid, data in sorted_analytics:
            tracker_badge = "🟢 ON" if data["tracker_enabled"] else "🔴 OFF"
            html_content += f"""
                        <tr>
                            <td class="adid-cell">{adid[:16]}...</td>
                            <td>{tracker_badge}</td>
                            <td>{data["purchases"]}</td>
                            <td>{data["items_purchased"]}</td>
                            <td class="revenue-cell">${data["revenue_with_coupon"]:.2f}</td>
                            <td style="color: #a0aec0; font-weight: 600;">${data["revenue_without_coupon"]:.2f}</td>
                            <td class="revenue-cell" style="font-weight: 700; font-size: 18px;">${data["total_revenue"]:.2f}</td>
                            <td class="savings-cell">${data["total_savings"]:.2f}</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
        """
    else:
        html_content += """
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <h3>No purchases yet</h3>
                    <p>Waiting for customers to make purchases...</p>
                </div>
        """
    
    html_content += """
            </div>
            
            <div class="table-container" style="margin-top: 30px;">
                <div class="table-header">
                    <h2>Product Performance Analytics</h2>
                </div>
    """
    
    if product_analytics:
        html_content += """
                <table>
                    <thead>
                        <tr>
                            <th rowspan="3">Product Name</th>
                            <th colspan="6" style="border-bottom: 1px solid rgba(255,255,255,0.2); background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">Tracker ON</th>
                            <th colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2); background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">Tracker OFF</th>
                            <th rowspan="3">Total Revenue</th>
                        </tr>
                        <tr>
                            <th colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2); background: rgba(240, 147, 251, 0.4);">WITH Coupon</th>
                            <th colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2); background: rgba(160, 174, 192, 0.4);">WITHOUT Coupon</th>
                            <th colspan="3" style="background: rgba(67, 233, 123, 0.3);">All Purchases</th>
                        </tr>
                        <tr>
                            <th style="background: rgba(240, 147, 251, 0.3);">Qty</th>
                            <th style="background: rgba(240, 147, 251, 0.3);">Revenue</th>
                            <th style="background: rgba(240, 147, 251, 0.3);">Savings</th>
                            <th style="background: rgba(160, 174, 192, 0.3);">Qty</th>
                            <th style="background: rgba(160, 174, 192, 0.3);">Revenue</th>
                            <th style="background: rgba(160, 174, 192, 0.3);">-</th>
                            <th style="background: rgba(67, 233, 123, 0.3);">Qty</th>
                            <th style="background: rgba(67, 233, 123, 0.3);">Revenue</th>
                            <th style="background: rgba(67, 233, 123, 0.3);">Savings</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # Sort by total revenue (highest first)
        sorted_products = sorted(
            product_analytics.items(), 
            key=lambda x: x[1]["tracker_on_with_coupon"]["revenue"] + x[1]["tracker_on_without_coupon"]["revenue"] + x[1]["tracker_off"]["revenue"], 
            reverse=True
        )
        
        for product_name, data in sorted_products:
            on_with = data["tracker_on_with_coupon"]
            on_without = data["tracker_on_without_coupon"]
            off = data["tracker_off"]
            total_revenue = on_with["revenue"] + on_without["revenue"] + off["revenue"]
            
            html_content += f"""
                        <tr>
                            <td style="font-weight: 600; text-align: left;">{product_name}</td>
                            <td>{on_with["quantity"]}</td>
                            <td class="revenue-cell">${on_with["revenue"]:.2f}</td>
                            <td class="savings-cell">${on_with["savings"]:.2f}</td>
                            <td>{on_without["quantity"]}</td>
                            <td style="color: #a0aec0; font-weight: 600;">${on_without["revenue"]:.2f}</td>
                            <td>-</td>
                            <td>{off["quantity"]}</td>
                            <td class="revenue-cell">${off["revenue"]:.2f}</td>
                            <td class="savings-cell">${off["savings"]:.2f}</td>
                            <td class="revenue-cell" style="font-weight: 700; font-size: 18px;">${total_revenue:.2f}</td>
                        </tr>
            """
        
        # Add totals row
        total_on_with_qty = sum(p["tracker_on_with_coupon"]["quantity"] for p in product_analytics.values())
        total_on_with_rev = sum(p["tracker_on_with_coupon"]["revenue"] for p in product_analytics.values())
        total_on_with_sav = sum(p["tracker_on_with_coupon"]["savings"] for p in product_analytics.values())
        total_on_without_qty = sum(p["tracker_on_without_coupon"]["quantity"] for p in product_analytics.values())
        total_on_without_rev = sum(p["tracker_on_without_coupon"]["revenue"] for p in product_analytics.values())
        total_off_qty = sum(p["tracker_off"]["quantity"] for p in product_analytics.values())
        total_off_rev = sum(p["tracker_off"]["revenue"] for p in product_analytics.values())
        total_off_sav = sum(p["tracker_off"]["savings"] for p in product_analytics.values())
        grand_total = total_on_with_rev + total_on_without_rev + total_off_rev
        
        html_content += f"""
                        <tr style="background: rgba(102, 126, 234, 0.15); font-weight: 700; border-top: 2px solid rgba(102, 126, 234, 0.5);">
                            <td style="text-align: left;">TOTAL</td>
                            <td>{total_on_with_qty}</td>
                            <td class="revenue-cell">${total_on_with_rev:.2f}</td>
                            <td class="savings-cell">${total_on_with_sav:.2f}</td>
                            <td>{total_on_without_qty}</td>
                            <td style="color: #a0aec0; font-weight: 700;">${total_on_without_rev:.2f}</td>
                            <td>-</td>
                            <td>{total_off_qty}</td>
                            <td class="revenue-cell">${total_off_rev:.2f}</td>
                            <td class="savings-cell">${total_off_sav:.2f}</td>
                            <td class="revenue-cell" style="font-size: 20px;">${grand_total:.2f}</td>
                        </tr>
                    </tbody>
                </table>
        """
    else:
        html_content += """
                <div class="empty-state">
                    <div class="empty-state-icon">📦</div>
                    <h3>No product data yet</h3>
                    <p>Product analytics will appear here once purchases are made...</p>
                </div>
        """
    
    html_content += """
            </div>
        </div>
        
        <button class="refresh-button" onclick="location.reload()">🔄 Refresh Data</button>
        
        <script>
            // Auto-refresh every 10 seconds
            setTimeout(() => location.reload(), 10000);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

