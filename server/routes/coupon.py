"""
Coupon and Purchase endpoints
"""
from fastapi import APIRouter
from datetime import datetime

from models import CouponRequest, CouponResponse, PurchaseRequest, PurchaseResponse, AnalyticsBatch
from config import coupon_history, purchase_history, analytics_events
from utils.helpers import generate_coupon_id, generate_purchase_id

router = APIRouter()

@router.post("/coupon", response_model=CouponResponse)
async def create_coupon(request: CouponRequest):
    """Create a discount coupon for a product"""
    print(f"[Server] Received coupon request:")
    print(f"  - ADID: {request.adid}")
    print(f"  - Product: {request.productName}")
    
    coupon_id = generate_coupon_id()
    discount = 0.2  # 20% discount
    
    coupon_record = {
        "couponId": coupon_id,
        "adid": request.adid,
        "productName": request.productName,
        "discount": discount,
        "timestamp": datetime.now().isoformat()
    }
    coupon_history.append(coupon_record)
    
    print(f"[Server] Sending coupon: {coupon_id} - {discount * 100}%")
    
    return CouponResponse(couponId=coupon_id, discount=discount)

@router.get("/coupons")
async def get_coupon_history():
    """Get all issued coupons (for debugging)"""
    return {
        "total": len(coupon_history),
        "coupons": coupon_history
    }

@router.post("/purchase", response_model=PurchaseResponse)
async def record_purchase(request: PurchaseRequest):
    """Record a purchase"""
    print(f"[Server] Received purchase:")
    print(f"  - ADID: {request.adid}")
    print(f"  - Items: {len(request.items)}")
    for item in request.items:
        print(f"    • {item.id} - {item.name}: ${item.finalPrice:.2f}")
    print(f"  - Total: ${request.total:.2f}")
    print(f"  - Tracker: {'ON' if request.trackerEnabled else 'OFF'}")
    
    purchase_id = generate_purchase_id()
    
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
    
    return PurchaseResponse(
        success=True,
        purchaseId=purchase_id,
        timestamp=datetime.now().isoformat()
    )

@router.get("/purchases")
async def get_purchase_history():
    """Get all purchases (for debugging)"""
    return {
        "total": len(purchase_history),
        "purchases": purchase_history
    }

@router.post("/analytics-events")
async def receive_analytics_events(batch: AnalyticsBatch):
    """Receive a batch of analytics events from SDK"""
    print(f"[Server] Received {len(batch.events)} events from ADID: {batch.adid}")
    
    for event in batch.events:
        event_record = {
            "adid": batch.adid,
            "eventType": event.eventType,
            "productId": event.productId,
            "productName": event.productName,
            "timestamp": event.timestamp,
            "viewDuration": event.viewDuration,
            "receivedAt": datetime.now().isoformat()
        }
        analytics_events.append(event_record)
        
        if event.viewDuration is not None:
            print(f"  - {event.eventType}: {event.productId} - {event.productName} (duration: {event.viewDuration}ms)")
        else:
            print(f"  - {event.eventType}: {event.productId} - {event.productName}")
    
    return {"success": True, "eventsReceived": len(batch.events)}

