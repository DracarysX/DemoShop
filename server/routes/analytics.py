"""
Analytics dashboard endpoints
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime
from typing import Dict, List
from collections import defaultdict
import json
import numpy as np

from config import analytics_events, purchase_history

router = APIRouter()

@router.get("/analytics-realtime", response_class=HTMLResponse)
async def get_realtime_analytics():
    """
    Display real-time analytics dashboard with event tracking
    """
    # Aggregate events by ADID
    adid_stats: Dict[str, Dict] = defaultdict(lambda: {
        "view_starts": 0,
        "view_ends": 0,
        "clicks": 0,
        "total_view_duration": 0,
        "products_viewed": set(),
        "products_clicked": set(),
        "last_activity": None
    })
    
    # Aggregate events by product
    product_stats: Dict[str, Dict] = defaultdict(lambda: {
        "clicks": 0,
        "total_view_duration": 0,
        "unique_adids": set()
    })
    
    # Track purchases by ADID
    adid_purchases: Dict[str, List[Dict]] = defaultdict(list)
    
    # Track product performance per ADID
    adid_product_performance: Dict[str, Dict[str, Dict]] = defaultdict(lambda: defaultdict(lambda: {
        "clicks": 0,
        "view_duration": 0,
        "purchased": 0,
        "revenue": 0.0
    }))
    
    for event in analytics_events:
        adid = event["adid"]
        product_id = event.get("productId", "unknown")
        product_name = event["productName"]
        event_type = event["eventType"]
        product_key = f"{product_id} - {product_name}"
        
        # Update last activity
        adid_stats[adid]["last_activity"] = event["receivedAt"]
        
        # Track by event type
        if event_type == "view_start":
            adid_stats[adid]["view_starts"] += 1
            adid_stats[adid]["products_viewed"].add(product_key)
            product_stats[product_key]["unique_adids"].add(adid)
        elif event_type == "view_end":
            adid_stats[adid]["view_ends"] += 1
            if event["viewDuration"] is not None:
                duration = event["viewDuration"]
                adid_stats[adid]["total_view_duration"] += duration
                product_stats[product_key]["total_view_duration"] += duration
                adid_product_performance[adid][product_key]["view_duration"] += duration
        elif event_type == "view":
            # Periodic view event (every 10 seconds of continuous viewing)
            if event["viewDuration"] is not None:
                duration = event["viewDuration"]
                adid_stats[adid]["total_view_duration"] += duration
                product_stats[product_key]["total_view_duration"] += duration
                adid_stats[adid]["products_viewed"].add(product_key)
                product_stats[product_key]["unique_adids"].add(adid)
                adid_product_performance[adid][product_key]["view_duration"] += duration
        elif event_type == "click":
            adid_stats[adid]["clicks"] += 1
            adid_stats[adid]["products_clicked"].add(product_key)
            product_stats[product_key]["clicks"] += 1
            adid_product_performance[adid][product_key]["clicks"] += 1
    
    # Aggregate purchases by ADID
    for purchase in purchase_history:
        adid = purchase["adid"]
        for item in purchase["items"]:
            product_id = item.get("id", "unknown")
            product_name = item["name"]
            product_key = f"{product_id} - {product_name}"
            
            # Update purchase stats in product performance
            adid_product_performance[adid][product_key]["purchased"] += 1
            adid_product_performance[adid][product_key]["revenue"] += item["finalPrice"]
            
            # Find if product already exists for this ADID
            existing = next((p for p in adid_purchases[adid] if p["product"] == product_key), None)
            if existing:
                existing["quantity"] += 1
                existing["revenue"] += item["finalPrice"]
                if item["discount"] > 0:
                    existing["discounted"] += 1
            else:
                adid_purchases[adid].append({
                    "product": product_key,
                    "quantity": 1,
                    "revenue": item["finalPrice"],
                    "discounted": 1 if item["discount"] > 0 else 0
                })
    
    # Generate HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Analytics Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <link rel="stylesheet" href="/static/css/common.css">
        <style>
            .container { max-width: 1400px; margin: 0 auto; }
            .header {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 32px;
                color: #2d3748;
                margin-bottom: 10px;
            }
            .header p {
                color: #718096;
                font-size: 16px;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .stat-card h3 {
                color: #718096;
                font-size: 14px;
                text-transform: uppercase;
                margin-bottom: 10px;
                font-weight: 600;
            }
            .stat-card .value {
                font-size: 36px;
                font-weight: bold;
                color: #2d3748;
            }
            table {
                width: 100%;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            th {
                background: #f1f5f9;
                color: #475569;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 15px;
                border-bottom: 1px solid #e2e8f0;
                color: #2d3748;
            }
            tr:last-child td { border-bottom: none; }
            tr:hover { background: #f7fafc; }
            .badge {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
            .badge-view { background: #e6fffa; color: #047857; }
            .badge-click { background: #fef3c7; color: #b45309; }
            .section-title {
                color: #0f172a;
                font-size: 24px;
                font-weight: 600;
                margin: 30px 0 15px 0;
            }
            .user-selector {
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .user-selector h3 {
                color: #2d3748;
                font-size: 18px;
                margin-bottom: 15px;
            }
            .user-selector select {
                width: 100%;
                padding: 12px;
                font-size: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background: white;
                color: #2d3748;
                cursor: pointer;
                outline: none;
            }
            .user-selector select:focus {
                border-color: #3b82f6;
            }
            #userPerformanceTable {
                margin-bottom: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/" class="back-link">← Back to Dashboard</a>
            
            <div class="header">
                <h1>🔥 Real-Time Analytics Dashboard</h1>
                <p>Auto-refreshes every 5 seconds • Last update: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Unique ADIDs</h3>
                    <div class="value">""" + str(len(adid_stats)) + """</div>
                </div>
            </div>
            
            <div class="user-selector">
                <h3>📊 User Product Performance</h3>
                <select id="adidSelector" onchange="updateUserPerformance()">"""
    
    if len(adid_stats) == 0:
        html_content += """
                    <option value="">No user activity yet</option>"""
    else:
        html_content += """
                    <option value="">Select a user (ADID) to view their performance...</option>"""
        # Add options for each ADID from analytics events
        for adid in sorted(adid_stats.keys(), key=lambda x: x):
            html_content += f"""
                    <option value="{adid}">{adid}</option>"""
    
    html_content += """
                </select>
            </div>
            
            <div id="userPerformanceTable" style="display: none;">
                <h3 id="userPerformanceTitle" class="section-title">User Product Performance</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Clicks</th>
                            <th>View Time</th>
                            <th>Purchased</th>
                            <th>Revenue</th>
                        </tr>
                    </thead>
                    <tbody id="userPerformanceBody">
                    </tbody>
                </table>
            </div>
            
            <div class="section-title">Product Performance</div>
            <table id="productTable">
                <thead>
                    <tr>
                        <th>Product</th>
                        <th>Clicks</th>
                        <th>View Time</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Show aggregated product performance
    for product in sorted(product_stats.keys(), key=lambda x: product_stats[x]["clicks"], reverse=True):
        stats = product_stats[product]
        total_clicks = stats["clicks"]
        total_view_seconds = stats["total_view_duration"] / 1000
        
        if total_clicks > 0 or total_view_seconds > 0:
            html_content += f"""
                    <tr>
                        <td><strong>{product}</strong></td>
                        <td>{total_clicks}</td>
                        <td>{total_view_seconds:.1f}s</td>
                    </tr>
            """
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <script>
            // Store product performance data for each ADID
            const adidProductPerformance = """
    
    # Convert adid_product_performance to JSON-safe format
    performance_data_json = {}
    for adid, products in adid_product_performance.items():
        performance_data_json[adid] = dict(products)
    
    html_content += json.dumps(performance_data_json)
    
    html_content += """;
            
            function updateUserPerformance() {
                const selector = document.getElementById('adidSelector');
                const selectedAdid = selector.value;
                const table = document.getElementById('userPerformanceTable');
                const tbody = document.getElementById('userPerformanceBody');
                
                // Store selection in localStorage
                if (selectedAdid) {
                    localStorage.setItem('selectedAdid', selectedAdid);
                } else {
                    localStorage.removeItem('selectedAdid');
                }
                
                if (!selectedAdid || !adidProductPerformance[selectedAdid]) {
                    table.style.display = 'none';
                    return;
                }
                
                table.style.display = 'block';
                
                const products = adidProductPerformance[selectedAdid];
                
                // Convert to array and sort by clicks + purchases (descending)
                const sortedProducts = Object.entries(products).sort((a, b) => {
                    const scoreA = a[1].clicks + (a[1].purchased * 10);
                    const scoreB = b[1].clicks + (b[1].purchased * 10);
                    return scoreB - scoreA;
                });
                
                let html = '';
                sortedProducts.forEach(([productKey, stats]) => {
                    const viewSeconds = (stats.view_duration / 1000).toFixed(1);
                    html += `
                        <tr>
                            <td><strong>${productKey}</strong></td>
                            <td>${stats.clicks}</td>
                            <td>${viewSeconds}s</td>
                            <td>${stats.purchased}</td>
                            <td>$${stats.revenue.toFixed(2)}</td>
                        </tr>
                    `;
                });
                
                if (html === '') {
                    html = '<tr><td colspan="5" style="text-align: center; color: #999;">No product interactions yet</td></tr>';
                }
                
                tbody.innerHTML = html;
            }
            
            // Restore selection on page load
            window.addEventListener('DOMContentLoaded', function() {
                const savedAdid = localStorage.getItem('selectedAdid');
                if (savedAdid) {
                    const selector = document.getElementById('adidSelector');
                    // Check if the option still exists
                    const option = Array.from(selector.options).find(opt => opt.value === savedAdid);
                    if (option) {
                        selector.value = savedAdid;
                        updateUserPerformance();
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/analytics", response_class=HTMLResponse)
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
            product_id = item.get("id", "unknown")
            product_name = item["name"]
            product_key = f"{product_id} - {product_name}"
            if tracker_enabled:
                product_analytics[product_key]["tracker_on_with_coupon"]["quantity"] += 1
                product_analytics[product_key]["tracker_on_with_coupon"]["revenue"] += final_price
                product_analytics[product_key]["tracker_on_with_coupon"]["savings"] += savings
            else:
                product_analytics[product_key]["tracker_off"]["quantity"] += 1
                product_analytics[product_key]["tracker_off"]["revenue"] += final_price
                product_analytics[product_key]["tracker_off"]["savings"] += savings
        
        # Process items WITHOUT coupons
        for item in non_discounted_items:
            analytics[adid]["total_revenue"] += item["finalPrice"]
            analytics[adid]["revenue_without_coupon"] += item["finalPrice"]
            analytics[adid]["items_purchased"] += 1
            
            # Product-level analytics
            product_id = item.get("id", "unknown")
            product_name = item["name"]
            product_key = f"{product_id} - {product_name}"
            if tracker_enabled:
                product_analytics[product_key]["tracker_on_without_coupon"]["quantity"] += 1
                product_analytics[product_key]["tracker_on_without_coupon"]["revenue"] += item["finalPrice"]
            else:
                product_analytics[product_key]["tracker_off"]["quantity"] += 1
                product_analytics[product_key]["tracker_off"]["revenue"] += item["finalPrice"]
    
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
                background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                min-height: 100vh;
                padding: 40px 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                color: #1e293b;
                margin-bottom: 40px;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            
            .header h1 {
                font-size: 48px;
                font-weight: 700;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 18px;
                opacity: 0.7;
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
                color: #1e293b;
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
                margin-bottom: 20px;
            }
            
            .table-header {
                background: white;
                color: #1e293b;
                padding: 30px;
                border-bottom: 2px solid #e2e8f0;
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
                color: #3b82f6;
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
                color: #3b82f6;
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
            <a href="/" class="back-link">← Back to Dashboard</a>
            
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
                <div class="stat-card">
                    <div class="stat-value">""" + str(purchases_with_coupon) + """</div>
                    <div class="stat-label">Purchases WITH Coupons</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">""" + str(purchases_without_coupon) + """</div>
                    <div class="stat-label">Purchases WITHOUT Coupons</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">""" + f"{tracker_on_percentage:.1f}%" + """</div>
                    <div class="stat-label">ADIDs with Tracker ON</div>
                </div>
            </div>
            
            <div class="table-container">
                <div class="table-header">
                    <h2>💰 Revenue Projection: 100% Tracker Adoption</h2>
                </div>
                <div style="padding: 30px; color: #1e293b;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px;">
                        <div style="text-align: center;">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Current Revenue</div>
                            <div style="font-size: 32px; font-weight: 700;">$""" + f"{current_total_revenue:.2f}" + """</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Projected Revenue (100%)</div>
                            <div style="font-size: 32px; font-weight: 700; color: #3b82f6;">$""" + f"{projected_revenue_100:.2f}" + """</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Additional Revenue</div>
                            <div style="font-size: 32px; font-weight: 700; color: #10b981;">+$""" + f"{additional_revenue:.2f}" + """</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 14px; opacity: 0.8; margin-bottom: 5px;">Increase</div>
                            <div style="font-size: 32px; font-weight: 700; color: #10b981;">+""" + f"{percentage_increase:.1f}%" + """</div>
                        </div>
                    </div>
                    <div style="background: #f8fafc; padding: 15px; border-radius: 10px; text-align: center; font-size: 16px; border: 1px solid #e2e8f0;">
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
            
            <div class="table-container">
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
                            <th colspan="6" style="border-bottom: 1px solid rgba(255,255,255,0.2); background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);">Tracker ON</th>
                            <th colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2); background: linear-gradient(135deg, #10b981 0%, #059669 100%);">Tracker OFF</th>
                            <th rowspan="3">Total Revenue</th>
                        </tr>
                        <tr>
                            <th colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2); background: rgba(59, 130, 246, 0.4);">WITH Coupon</th>
                            <th colspan="3" style="border-bottom: 1px solid rgba(255,255,255,0.2); background: rgba(148, 163, 184, 0.4);">WITHOUT Coupon</th>
                            <th colspan="3" style="background: rgba(16, 185, 129, 0.3);">All Purchases</th>
                        </tr>
                        <tr>
                            <th style="background: rgba(59, 130, 246, 0.3);">Qty</th>
                            <th style="background: rgba(59, 130, 246, 0.3);">Revenue</th>
                            <th style="background: rgba(59, 130, 246, 0.3);">Savings</th>
                            <th style="background: rgba(148, 163, 184, 0.3);">Qty</th>
                            <th style="background: rgba(148, 163, 184, 0.3);">Revenue</th>
                            <th style="background: rgba(148, 163, 184, 0.3);">-</th>
                            <th style="background: rgba(16, 185, 129, 0.3);">Qty</th>
                            <th style="background: rgba(16, 185, 129, 0.3);">Revenue</th>
                            <th style="background: rgba(16, 185, 129, 0.3);">Savings</th>
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

