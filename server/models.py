"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel
from typing import List

class CouponRequest(BaseModel):
    adid: str
    productName: str

class CouponResponse(BaseModel):
    couponId: str
    discount: float

class PurchaseItem(BaseModel):
    id: str
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

class AnalyticsEvent(BaseModel):
    eventType: str  # 'view', 'click'
    productId: str
    productName: str
    timestamp: int
    viewDuration: int | None = None

class AnalyticsBatch(BaseModel):
    adid: str
    events: List[AnalyticsEvent]

